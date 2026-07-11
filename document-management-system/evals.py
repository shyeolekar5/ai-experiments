#!/usr/bin/env python3
"""
run_evals.py
============
Evaluates a config (typically evals/winners.json) against ground truth.
Measures field-level precision/recall per document type, confidence
calibration, and cost.  Writes a versioned result file and optionally
promotes the config to "live" status.

Version control:
  - Every eval run writes a new versioned JSON to evals/configs/
  - The version number increments automatically based on existing files
  - evals/winners.json is updated with eval_results after a run
  - Nothing is ever deleted — full history is in git

Usage:
  python scripts/run_evals.py --api-key YOUR_KEY
  python scripts/run_evals.py --api-key YOUR_KEY --config evals/winners.json
  python scripts/run_evals.py --api-key YOUR_KEY --config evals/configs/experiment_v1_model_comparison_20261001_120000.json
  python scripts/run_evals.py --api-key YOUR_KEY --promote   # write status=live if passes
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests

# ── Paths ──────────────────────────────────────────────────────────────
ROOT        = Path(r"C:\document-management-system")
TEST_DOCS   = ROOT / "test_samples"
EVALS_DIR   = ROOT / "evals"
CONFIGS_DIR = EVALS_DIR / "configs"
RESULTS_DIR = EVALS_DIR / "results"
GT_FILE     = TEST_DOCS / "ground_truth.json"
WINNERS_FILE= EVALS_DIR / "winners.json"

for d in [EVALS_DIR, CONFIGS_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

GEMINI_BASE = ("https://generativelanguage.googleapis.com/v1beta/models"
               "/{model}:generateContent")

# ── Doc config (mirrors demo_app.py) ──────────────────────────────────
DOC_CONFIG = {
    "Invoice": {
        "description": (
            "A demand for payment. The vendor has delivered goods or services and is now "
            "requesting settlement. If there is a Total Due and a billing reference number, "
            "it is almost certainly an invoice."
        ),
        "anchors": ["INVOICE", "TAX INVOICE", "SERV-", "INV-"],
        "fields": [
            {"key":"invoice_number","type":"string","required":True,
             "description":"The unique reference number, format SERV-XXXX or INV-XXXX, near the top."},
            {"key":"customer_name", "type":"string","required":True,
             "description":"The company being billed, under Client Information after the vendor block."},
            {"key":"total_amount",  "type":"number","required":True,
             "description":"Final amount owed on the Total Due line. Number only."},
        ],
    },
    "Purchase Order": {
        "description": (
            "An authorisation to spend, issued before goods are delivered. "
            "A PO flows from buyer to supplier. Often arrives as a fax scan."
        ),
        "anchors": ["PURCHASE ORDER", "P.O.", "REQUISITION", "PO-"],
        "fields": [
            {"key":"po_number",      "type":"string", "required":True,
             "description":"Purchase order reference number, format PO-XXXXX."},
            {"key":"ship_to_company","type":"string", "required":False,
             "description":"Name of the company receiving goods, under Ship To."},
            {"key":"quantity",       "type":"integer","required":True,
             "description":"Total units ordered. Largest single quantity if multiple items."},
        ],
    },
    "Complaint": {
        "description": (
            "A customer expressing dissatisfaction and demanding resolution. "
            "Negative tone, named customer, specific problem."
        ),
        "anchors": ["COMPLAINT", "GRIEVANCE", "FEEDBACK", "TICKET"],
        "fields": [
            {"key":"ticket_id",    "type":"string","required":False,
             "description":"Ticket reference, format TS-COMPLAINT-XXXX. Null if absent."},
            {"key":"customer_name","type":"string","required":True,
             "description":"Full name of the customer who submitted the complaint."},
            {"key":"issue_summary","type":"string","required":True,
             "description":"One or two sentence summary of the core problem. Factual."},
        ],
    },
    "Contract": {
        "description": (
            "A legally binding agreement creating obligations between named parties. "
            "Both sides sign. Multi-page with WHEREAS recitals and governing law section."
        ),
        "anchors": ["AGREEMENT", "CONTRACT", "TERMS AND CONDITIONS", "WHEREAS"],
        "fields": [
            {"key":"contract_id",   "type":"string","required":False,
             "description":"Contract reference number near the top."},
            {"key":"parties",       "type":"string","required":True,
             "description":"Names of all parties in the opening clause. Return both names."},
            {"key":"effective_date","type":"string","required":True,
             "description":"Date the contract takes effect, in the opening paragraph."},
            {"key":"governing_law", "type":"string","required":False,
             "description":"Jurisdiction in the Governing Law section, near the end."},
            {"key":"contract_value","type":"number","required":False,
             "description":"Total contract value in dollars. Number only."},
        ],
    },
}

# ── Helpers ────────────────────────────────────────────────────────────
def load_doc(path):
    ext  = Path(path).suffix.lower()
    mime = {".pdf":"application/pdf",".png":"image/png",
            ".jpg":"image/jpeg",".jpeg":"image/jpeg"}.get(ext,"application/octet-stream")
    return Path(path).read_bytes(), mime

def b64(data): return base64.b64encode(data).decode()

def call_gemini(api_key, model, payload, timeout=60):
    url = GEMINI_BASE.format(model=model)
    t0  = time.time()
    for attempt in range(2):
        try:
            r = requests.post(f"{url}?key={api_key}", json=payload,
                              headers={"Content-Type":"application/json"}, timeout=timeout)
            lat = time.time()-t0
            if r.status_code == 200:
                return r.json(), lat, None
            if r.status_code == 429:
                print(f"    [rate limit, waiting 15s...]")
                time.sleep(15); continue
            return None, lat, f"HTTP {r.status_code}: {r.text[:300]}"
        except Exception as e:
            if attempt == 0:
                print(f"    [timeout, retrying...]")
                time.sleep(3); continue
            return None, time.time()-t0, str(e)
    return None, time.time()-t0, "Max retries exceeded"

def gemini_cost(usage, model):
    inp = usage.get("promptTokenCount",0)
    out = usage.get("candidatesTokenCount",0)
    if "pro" in model and "flash" not in model:
        return (inp/1e6)*1.25+(out/1e6)*5.00
    elif "8b" in model:
        return (inp/1e6)*0.0375+(out/1e6)*0.15
    return (inp/1e6)*0.075+(out/1e6)*0.30

def next_version():
    """Find the next version number based on existing eval configs."""
    existing = list(CONFIGS_DIR.glob("eval_v*.json"))
    if not existing: return 1
    nums = []
    for f in existing:
        m = re.match(r"eval_v(\d+)_", f.name)
        if m: nums.append(int(m.group(1)))
    return max(nums)+1 if nums else 1

def judge_semantic_field(api_key, model, field_key, extracted, expected):
    """
    LLM-as-judge for semantic fields (issue_summary, parties, governing_law).
    Returns (is_correct: bool, reason: str).
    Falls back to substring match if the judge call fails.
    """
    prompt = (
        f"Evaluate whether this AI extraction is correct.\n\n"
        f"Field: {field_key}\n"
        f"Expected: {expected}\n"
        f"Extracted: {extracted}\n\n"
        f"Does the extracted value correctly capture the same core information "
        f"as the expected value, even if phrased differently? "
        f"A partial answer that misses key facts should be marked incorrect."
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "object",
                "properties": {
                    "correct": {"type": "BOOLEAN"},
                    "reason":  {"type": "STRING"},
                },
                "required": ["correct", "reason"],
            },
            "temperature": 0.0,
        },
    }
    resp, _, err = call_gemini(api_key, model, payload, timeout=20)
    if err or not resp:
        # Fallback to substring match
        ev = str(extracted).lower(); ex = str(expected).lower()
        return (ex in ev or ev in ex), f"judge unavailable ({err}), substring fallback"
    try:
        raw    = resp["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw)
        return bool(parsed["correct"]), parsed.get("reason", "")
    except Exception as e:
        ev = str(extracted).lower(); ex = str(expected).lower()
        return (ex in ev or ev in ex), f"judge parse error ({e}), substring fallback"


def field_match(extracted_val, expected_val, field_type, is_semantic=False,
                api_key=None, model=None, field_key=""):
    """
    Classify extraction outcome as TP / FP / FN / TN / HAL.
    Semantic fields (issue_summary, parties, governing_law) use LLM-as-judge.
    Returns (outcome, extracted_str, expected_str, detail)
    """
    if expected_val is None:
        if extracted_val is None or str(extracted_val).strip() == "":
            return "TN",  "null",             "null (absent)",  "correctly returned null"
        else:
            return "HAL", str(extracted_val), "null (absent)",  "hallucinated — field not in document"
    if extracted_val is None or str(extracted_val).strip() == "":
        return "FN", repr(extracted_val), str(expected_val), "field exists but AI returned null"
    ev = str(extracted_val).strip()
    ex = str(expected_val).strip()

    # Semantic fields: use LLM-as-judge
    if is_semantic and api_key and model:
        correct, reason = judge_semantic_field(api_key, model, field_key, ev, ex)
        return ("TP" if correct else "FP"), ev, ex, f"[LLM judge] {reason}"

    if field_type == "number":
        try:
            ef = float(re.sub(r"[,$\s]","", ev))
            xf = float(ex)
            pct = abs(ef-xf)/max(abs(xf),1)*100
            if pct < 1.0:
                return "TP", ev, ex, f"within 1% ({pct:.2f}% delta)"
            else:
                return "FP", ev, ex, f"wrong number ({pct:.1f}% delta)"
        except Exception as e:
            return "FP", ev, ex, f"could not parse as number: {e}"
    elif field_type == "integer":
        try:
            ei = int(ev); xi = int(ex)
            if ei == xi:
                return "TP", ev, ex, "exact match"
            else:
                return "FP", ev, ex, f"wrong integer (got {ei}, expected {xi})"
        except Exception as e:
            return "FP", ev, ex, f"could not parse as integer: {e}"
    else:
        ev_l = ev.lower(); ex_l = ex.lower()
        if ex_l in ev_l:
            return "TP", ev, ex, "expected value found in extracted"
        elif ev_l in ex_l:
            return "TP", ev, ex, "extracted is substring of expected"
        else:
            words_ex = set(ex_l.split()); words_ev = set(ev_l.split())
            missing = words_ex - words_ev; extra = words_ev - words_ex
            detail  = ""
            if missing: detail += f"missing words: {', '.join(sorted(missing)[:5])}. "
            if extra:   detail += f"extra words: {', '.join(sorted(extra)[:5])}."
            return "FP", ev, ex, detail.strip() or "strings do not match"


def score_extraction(extracted, doc_type, expected, api_key=None, model=None):
    """
    Score all fields. Returns (field_results, metrics).
    Semantic fields (semantic=True in DOC_CONFIG) use LLM-as-judge.
    Precision = TP/(TP+FP)  Recall = TP/(TP+FN)  F1 = harmonic mean
    """
    fields  = DOC_CONFIG[doc_type]["fields"]
    results = {}
    tp = fp = fn = tn = hal = 0
    for f in fields:
        k      = f["key"]
        ext    = (extracted or {}).get(k)
        exp    = expected.get(k)
        is_sem = f.get("semantic", False)
        outcome, ext_s, exp_s, detail = field_match(
            ext, exp, f["type"],
            is_semantic=is_sem, api_key=api_key, model=model, field_key=k)
        results[k] = {
            "outcome":  outcome, "extracted": ext_s, "expected": exp_s,
            "detail":   detail,  "required":  f.get("required", False),
            "type":     f["type"], "semantic": is_sem,
        }
        if   outcome=="TP":  tp  += 1
        elif outcome=="FP":  fp  += 1
        elif outcome=="FN":  fn  += 1
        elif outcome=="TN":  tn  += 1
        elif outcome=="HAL": hal += 1
    precision = tp/(tp+fp) if (tp+fp)>0 else (1.0 if fn==0 else 0.0)
    recall    = tp/(tp+fn) if (tp+fn)>0 else (1.0 if fn==0 else 0.0)
    f1        = (2*precision*recall/(precision+recall)) if (precision+recall)>0 else 0.0
    metrics   = {"precision":precision,"recall":recall,"f1":f1,
                 "tp":tp,"fp":fp,"fn":fn,"tn":tn,"hallucinations":hal}
    return results, metrics


def print_doc_result(fname, doc_type, field_results, metrics, conf, lat, cost):
    """Print full field-by-field breakdown."""
    overall = "✓" if metrics["precision"]>=0.8 and metrics["recall"]>=0.7 else "✗"
    print(f"    {overall} {fname}  [{doc_type}]")
    print(f"       precision={metrics['precision']:.0%}  recall={metrics['recall']:.0%}  "
          f"f1={metrics['f1']:.0%}  conf={conf:.0%}  lat={lat:.1f}s  cost=${cost:.5f}")
    print(f"       TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}  "
          f"TN={metrics['tn']}  HAL={metrics['hallucinations']}")
    print()
    ICONS = {"TP":"✓ TP ","FP":"✗ FP ","FN":"✗ FN ","TN":"– TN ","HAL":"⚠ HAL"}
    for field, fr in field_results.items():
        outcome = fr["outcome"]
        req     = " [required]" if fr.get("required") else " [optional]"
        print(f"       {ICONS.get(outcome,'?    ')} {field}{req}")
        if outcome == "TP":
            print(f"              extracted: '{fr['extracted']}'")
            print(f"              expected:  '{fr['expected']}' — {fr['detail']}")
        elif outcome in ("FP","FN"):
            print(f"              extracted: '{fr['extracted']}'")
            print(f"              expected:  '{fr['expected']}'")
            print(f"              why:       {fr['detail']}")
        elif outcome == "TN":
            print(f"              {fr['detail']}")
        elif outcome == "HAL":
            print(f"              extracted: '{fr['extracted']}' ← HALLUCINATED")
            print(f"              expected:  {fr['detail']}")
        print()

def run_single_document(api_key, model, call_mode, doc_type, fpath, mime,
                        data, cfg, chunk_config=None, rag_strategy="field_targeted"):
    """
    Run classify + extract on one document using the winner config.
    Returns (extracted_fields, confidence, latency, cost, tokens, classify_resp).
    """
    t0 = time.time()
    total_cost, total_tok = 0.0, 0

    # ── Classify ──────────────────────────────────────────────────────
    ctx_lines = []
    for dt, dcfg in DOC_CONFIG.items():
        kws = ", ".join(f"'{a}'" for a in dcfg["anchors"])
        ctx_lines.append(f"  {dt}:\n    {dcfg['description'][:120]}\n    Keywords: {kws}")
    ctx = "\n".join(ctx_lines)

    cls_payload = {
        "contents":[{"parts":[
            {"text":f"Classify this document.\n\nKnown types:\n{ctx}"},
            {"inlineData":{"mimeType":mime,"data":b64(data)}}
        ]}],
        "systemInstruction":{"parts":[{"text":
            "You are a document classification specialist. "
            "Return JSON with doc_type and confidence."}]},
        "generationConfig":{
            "responseMimeType":"application/json","temperature":0.0,
            "responseSchema":{"type":"object",
                "properties":{"doc_type":{"type":"STRING"},"confidence":{"type":"NUMBER"}},
                "required":["doc_type","confidence"]}}
    }
    cls_resp, cls_lat, cls_err = call_gemini(api_key, model, cls_payload)
    print(f"    Classified in {cls_lat:.1f}s" if not cls_err else f"    Classify error: {cls_err}")
    if cls_err:
        return None, 0.0, time.time()-t0, 0.0, 0, cls_err

    cls_raw    = cls_resp["candidates"][0]["content"]["parts"][0]["text"]
    cls_parsed = json.loads(cls_raw)
    detected   = cls_parsed.get("doc_type","UNKNOWN")
    cls_usage  = cls_resp.get("usageMetadata",{})
    total_cost+= gemini_cost(cls_usage, model)
    total_tok += cls_usage.get("promptTokenCount",0)+cls_usage.get("candidatesTokenCount",0)

    if detected not in DOC_CONFIG:
        return None, 0.0, time.time()-t0, total_cost, total_tok, f"Unknown type: {detected}"

    actual_cfg = DOC_CONFIG[detected]
    time.sleep(1)

    # ── Extract (with optional RAG for long PDFs) ─────────────────────
    props = {}
    for f in actual_cfg["fields"]:
        jt = "INTEGER" if f["type"]=="integer" else "NUMBER" if f["type"]=="number" else "STRING"
        props[f["key"]] = {"type":jt,"description":f["description"]}
    props["_confidence"] = {"type":"NUMBER","description":"Confidence 0-1"}

    # Check if this is a long PDF that should use RAG
    use_rag = False
    context_text = ""
    if mime == "application/pdf" and chunk_config:
        try:
            import pypdf, io as _io
            reader    = pypdf.PdfReader(_io.BytesIO(data))
            page_count= len(reader.pages)
            if page_count > 10:
                use_rag = True
                full_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                size, overlap = chunk_config.get("size",500), chunk_config.get("overlap",50)
                words  = full_text.split()
                chunks = []
                i = 0
                while i < len(words):
                    chunks.append(" ".join(words[i:i+size]))
                    i += size-overlap

                # Embed and retrieve
                embed_url = ("https://generativelanguage.googleapis.com/v1beta/models"
                             "/gemini-embedding-001:embedContent")
                def get_emb(text):
                    for _ in range(3):
                        try:
                            r = requests.post(f"{embed_url}?key={api_key}",
                                json={"model":"models/gemini-embedding-001",
                                      "content":{"parts":[{"text":text[:8000]}]}},
                                headers={"Content-Type":"application/json"}, timeout=15)
                            if r.status_code == 200:
                                data = r.json()
                            if "embeddings" in data and data["embeddings"]:
                                return data["embeddings"][0]["values"]
                            if "embedding" in data:
                                return data["embedding"]["values"]
                            return None
                            time.sleep(2)
                        except: time.sleep(2)
                    return None

                def csim(a,b):
                    if not a or not b: return 0.0
                    d=sum(x*y for x,y in zip(a,b))
                    return d/(sum(x*x for x in a)**0.5*sum(x*x for x in b)**0.5+1e-9)

                chunk_embeds = [get_emb(c) for c in chunks]

                if rag_strategy == "field_targeted":
                    ctx_parts = []
                    for f in actual_cfg["fields"]:
                        q_emb = get_emb(f"What is the {f['key']}? {f['description']}")
                        sims  = sorted([(csim(q_emb,ce),i) for i,ce in enumerate(chunk_embeds) if ce], reverse=True)
                        top   = " ".join(chunks[i] for _,i in sims[:3])
                        ctx_parts.append(f"[For field '{f['key']}']:\n{top[:1500]}")
                    context_text = "\n\n".join(ctx_parts)
                else:
                    q_emb = get_emb(f"Extract {', '.join(f['key'] for f in actual_cfg['fields'])} from this {detected}")
                    sims  = sorted([(csim(q_emb,ce),i) for i,ce in enumerate(chunk_embeds) if ce], reverse=True)
                    context_text = " ".join(chunks[i] for _,i in sims[:5])
        except Exception as e:
            pass  # Fall through to full-doc extraction

    if use_rag and context_text:
        user_text = (f"Extract the requested fields from these retrieved sections of a {detected}:\n\n"
                     f"{context_text}")
    else:
        user_text = f"Extract the requested fields from this {detected} document."

    ext_payload = {
        "contents":[{"parts":[
            {"text": user_text},
            *([] if (use_rag and context_text) else
              [{"inlineData":{"mimeType":mime,"data":b64(data)}}])
        ]}],
        "systemInstruction":{"parts":[{"text":
            f"You are a specialist extracting {detected} fields. "
            f"{actual_cfg['description']} Return only valid JSON."}]},
        "generationConfig":{
            "responseMimeType":"application/json",
            "responseSchema":{"type":"object","properties":props,"required":list(props.keys())}}
    }
    ext_resp, ext_lat, ext_err = call_gemini(api_key, model, ext_payload)
    if ext_err:
        return None, 0.0, time.time()-t0, total_cost, total_tok, ext_err

    ext_raw  = ext_resp["candidates"][0]["content"]["parts"][0]["text"]
    extr     = json.loads(ext_raw)
    conf     = float(extr.pop("_confidence",0.5))
    ext_usage= ext_resp.get("usageMetadata",{})
    total_cost += gemini_cost(ext_usage, model)
    total_tok  += ext_usage.get("promptTokenCount",0)+ext_usage.get("candidatesTokenCount",0)

    return extr, conf, time.time()-t0, total_cost, total_tok, None


# ══════════════════════════════════════════════════════════════════════
# MAIN EVAL
# ══════════════════════════════════════════════════════════════════════
def run_evals(api_key, config_path, promote=False):
    # Load config
    cfg_file = Path(config_path)
    if not cfg_file.exists():
        print(f"✗ Config not found: {cfg_file}")
        sys.exit(1)
    config = json.loads(cfg_file.read_text())
    print(f"\n{'='*65}")
    print(f"EVAL RUNNER")
    print(f"Config: {cfg_file.name}")
    print(f"Model:  {config.get('model','gemini-2.5-flash')}")
    print(f"Call mode: {config.get('call_mode','one_call')}")
    print(f"RAG strategy: {config.get('retrieval_strategy','field_targeted')}")
    print(f"Chunk: size={config.get('chunk_config',{}).get('size',500)} "
          f"overlap={config.get('chunk_config',{}).get('overlap',50)}")
    print('='*65)

    model        = config.get("model","gemini-2.5-flash")
    call_mode    = config.get("call_mode","one_call")
    chunk_config = config.get("chunk_config",{"size":500,"overlap":50})
    rag_strategy = config.get("retrieval_strategy","field_targeted")

    # Load ground truth
    if not GT_FILE.exists():
        print(f"✗ Ground truth not found: {GT_FILE}")
        sys.exit(1)
    gt   = json.loads(GT_FILE.read_text())
    docs = gt["documents"]

    # Check documents exist
    missing = [d["filename"] for d in docs if not (TEST_DOCS/d["filename"]).exists()]
    if missing:
        print(f"✗ Missing documents: {missing}")
        sys.exit(1)

    print(f"\nEvaluating {len(docs)} documents...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version   = next_version()

    doc_results   = {}
    all_precisions= {}
    total_cost    = 0.0
    total_tokens  = 0
    total_latency = 0.0

    for doc in docs:
        fname    = doc["filename"]
        doc_type = doc["doc_type"]
        expected = doc["expected"]
        fpath    = TEST_DOCS / fname
        print(f"\n  Processing: {fname} ({doc_type})")

        data, mime = load_doc(fpath)
        cfg        = DOC_CONFIG.get(doc_type,{})

        extr, conf, lat, cost, tok, err = run_single_document(
            api_key, model, call_mode, doc_type, fpath, mime,
            data, cfg, chunk_config, rag_strategy)

        total_cost    += cost
        total_tokens  += tok
        total_latency += lat

        if err or extr is None:
            print(f"    ✗ Error: {err}")
            doc_results[fname] = {
                "doc_type":doc_type,"error":err,"precision":0.0,
                "confidence":0.0,"latency":lat,"cost":cost,
            }
            if doc_type not in all_precisions:
                all_precisions[doc_type] = []
            all_precisions[doc_type].append(0.0)
            continue

        field_scores, metrics = score_extraction(extr, doc_type, expected, api_key=api_key, model=model)
        if doc_type not in all_precisions:
            all_precisions[doc_type] = []
        all_precisions[doc_type].append(metrics["precision"])

        doc_results[fname] = {
            "doc_type":  doc_type,
            "metrics":   metrics,
            "confidence":conf,
            "latency":   lat,
            "cost":      cost,
            "tokens":    tok,
            "fields":    field_scores,
            "extracted": extr,
        }

        print_doc_result(fname, doc_type, field_scores, metrics, conf, lat, cost)

        time.sleep(3)

    # ── Aggregate metrics ──────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("EVAL RESULTS SUMMARY")
    print('='*65)

    # Per doc type
    type_metrics = {}
    for dt, precisions in all_precisions.items():
        avg = sum(p for p in precisions)/len(precisions) if precisions else 0.0
        type_metrics[dt] = {"avg_precision":avg,"n_docs":len(precisions)}
        print(f"  {dt}: avg precision={avg:.0%} ({len(precisions)} docs)")

    overall = sum(r.get("metrics",{}).get("precision",0) for r in doc_results.values())/max(len(doc_results),1)
    print(f"\n  Overall precision:  {overall:.0%}")
    print(f"  Total cost:         ${total_cost:.5f}")
    print(f"  Total tokens:       {total_tokens:,}")
    print(f"  Total latency:      {total_latency:.1f}s")
    print(f"  Avg latency/doc:    {total_latency/max(len(docs),1):.1f}s")

    # Confidence calibration
    print(f"\n  Confidence calibration:")
    bands = [(0.0,0.7),(0.7,0.8),(0.8,0.9),(0.9,1.01)]
    for lo, hi in bands:
        in_band = [(r["confidence"],r.get("metrics",{}).get("precision",0))
                   for r in doc_results.values()
                   if lo <= r.get("confidence",0) < hi and "metrics" in r]
        if in_band:
            avg_conf = sum(c for c,_ in in_band)/len(in_band)
            avg_prec = sum(p for _,p in in_band)/len(in_band)
            print(f"    Confidence {lo:.0%}–{hi:.0%}: avg actual precision={avg_prec:.0%} "
                  f"(n={len(in_band)}, avg conf={avg_conf:.0%})")

    # Promotion check
    # Pass criteria: overall precision >= 85%, no doc type below 75%
    pass_threshold = 0.85
    min_type_threshold = 0.75
    passed = (overall >= pass_threshold and
              all(v["avg_precision"] >= min_type_threshold
                  for v in type_metrics.values()))

    print(f"\n  Promotion check:")
    print(f"    Overall ≥ {pass_threshold:.0%}: {'✓' if overall >= pass_threshold else '✗'} ({overall:.0%})")
    for dt, m in type_metrics.items():
        ok = m["avg_precision"] >= min_type_threshold
        print(f"    {dt} ≥ {min_type_threshold:.0%}: {'✓' if ok else '✗'} ({m['avg_precision']:.0%})")
    print(f"\n  → {'✓ PASSES promotion criteria' if passed else '✗ FAILS promotion criteria'}")

    # ── Write versioned eval result ────────────────────────────────────
    eval_result = {
        "eval_version":    version,
        "timestamp":       timestamp,
        "config_file":     str(cfg_file),
        "model":           model,
        "call_mode":       call_mode,
        "chunk_config":    chunk_config,
        "rag_strategy":    rag_strategy,
        "overall_precision": overall,
        "type_metrics":    type_metrics,
        "total_cost":      total_cost,
        "total_tokens":    total_tokens,
        "total_latency":   total_latency,
        "passes_promotion":passed,
        "documents":       doc_results,
        "promotion_criteria": {
            "overall_threshold": pass_threshold,
            "min_type_threshold": min_type_threshold,
        },
    }

    eval_file = CONFIGS_DIR / f"eval_v{version}_{timestamp}.json"
    eval_file.write_text(json.dumps(eval_result, indent=2, default=str))
    print(f"\n  ✓ Eval saved: {eval_file.name}")

    # ── Update winners.json with eval results ─────────────────────────
    if cfg_file == WINNERS_FILE or promote:
        config["eval_results"] = {
            "version":           version,
            "timestamp":         timestamp,
            "overall_precision": overall,
            "type_metrics":      type_metrics,
            "total_cost":        total_cost,
            "passes_promotion":  passed,
        }
        if passed and promote:
            config["status"] = "live"
            print(f"  ✓ Config promoted to 'live' status")
        elif not passed:
            config["status"] = "eval_failed"
            print(f"  ✗ Config NOT promoted — below precision threshold")
        cfg_file.write_text(json.dumps(config, indent=2))
        print(f"  ✓ Updated: {cfg_file.name}")

    # ── Version history ────────────────────────────────────────────────
    print(f"\n  Version history (evals/configs/eval_v*.json):")
    eval_files = sorted(CONFIGS_DIR.glob("eval_v*.json"))
    for ef in eval_files[-5:]:  # show last 5
        try:
            ec = json.loads(ef.read_text())
            passed_str = "✓ PASS" if ec.get("passes_promotion") else "✗ FAIL"
            print(f"    v{ec.get('eval_version','?')} {ec.get('timestamp','?')} "
                  f"precision={ec.get('overall_precision',0):.0%} {passed_str}")
        except:
            print(f"    {ef.name} (unreadable)")

    return eval_result


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="Eval runner for AI pipeline configs")
    parser.add_argument("--api-key",  required=True, help="Gemini API key")
    parser.add_argument("--config",   default=str(WINNERS_FILE),
                        help="Path to config JSON (default: evals/winners.json)")
    parser.add_argument("--promote",  action="store_true",
                        help="Promote to 'live' status if eval passes")
    args = parser.parse_args()

    result = run_evals(args.api_key, args.config, promote=args.promote)

    print(f"\n{'='*65}")
    if result["passes_promotion"]:
        print("✓ Eval passed. Run with --promote to mark this config as live.")
    else:
        print("✗ Eval failed. Review field-level results above.")
        print("  Common fixes:")
        print("  - Check field descriptions in Document Types")
        print("  - Review ground truth values in test_samples/ground_truth.json")
        print("  - Run experiments again with --experiments flag to retest")

if __name__ == "__main__":
    main()