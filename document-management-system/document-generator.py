"""
document-generator-v2.py
========================
Generates test documents for the AI Document Pipeline demo and eval suite.

Outputs (in ./test_samples/):
  Documents:
    invoice_90211_digital.pdf     — Fast-Track test (text-layer PDF)
    fax_scan_48291.jpg            — GenAI test (image / fax scan)
    customer_complaint.png        — GenAI test (screenshot image)
    contract_TECH-2026-001.pdf    — GenAI + RAG test (multi-page PDF)

  Ground truth (for eval runner):
    ground_truth.json             — expected field values per document

Run:
    pip install reportlab pillow pypdf
    python document-generator-v2.py
"""

import json
import os
import sys
import subprocess

# ── Dependency bootstrap ───────────────────────────────────────────────
def ensure(*packages):
    for pkg, imp in packages:
        try:
            __import__(imp)
        except ImportError:
            print(f"[+] Installing {pkg}…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg,
                                   "--break-system-packages", "-q"])
            print(f"[✓] {pkg} installed.")

ensure(("reportlab","reportlab"), ("pillow","PIL"), ("pypdf","pypdf"))

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import pypdf

os.makedirs("test_samples", exist_ok=True)

W, H = letter   # 612 x 792 pts

# ── Shared styles ─────────────────────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()
    title  = ParagraphStyle('T', parent=styles['Normal'],
                            fontName='Helvetica-Bold', fontSize=22,
                            textColor=colors.HexColor("#1e1b4b"), spaceAfter=10)
    h2     = ParagraphStyle('H2', parent=styles['Normal'],
                            fontName='Helvetica-Bold', fontSize=13,
                            textColor=colors.HexColor("#1e1b4b"), spaceAfter=6)
    body   = ParagraphStyle('B', parent=styles['Normal'],
                            fontName='Helvetica', fontSize=10,
                            textColor=colors.HexColor("#334155"), leading=14)
    bold   = ParagraphStyle('Bo', parent=body, fontName='Helvetica-Bold')
    small  = ParagraphStyle('S', parent=body, fontSize=9,
                            textColor=colors.HexColor("#64748b"))
    return title, h2, body, bold, small


# ═══════════════════════════════════════════════════════════════════════
# 1. INVOICE — Fast-Track test (text-layer PDF)
#    Pipeline should: anchor-match "INVOICE", run regex, auto-approve
# ═══════════════════════════════════════════════════════════════════════
def create_invoice():
    path = "test_samples/invoice_90211_digital.pdf"
    print(f"\n[+] Generating invoice PDF: {path}")

    title, h2, body, bold, small = get_styles()
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=40, bottomMargin=40)
    story = []

    # ── Header ──
    story.append(Paragraph("INVOICE", title))
    story.append(Paragraph("<b>Contract ID:</b> SERV-2026-88291", bold))
    story.append(Paragraph("<b>Date:</b> November 02, 2026", body))
    story.append(Paragraph("<b>Governing Laws:</b> Canada", body))
    story.append(Spacer(1, 18))

    # ── Vendor / Client — each on its OWN labelled row ──
    # Layout: label row then value row, so text extraction is deterministic.
    # The customer_name regex keys off "Client Information\n<vendor line>\n...<client>"
    info_data = [
        [Paragraph("<b>Vendor Information</b>", bold),
         Paragraph("<b>Client Information</b>", bold)],
        [Paragraph("TechStart Inc.<br/>100 Enterprise Way<br/>Toronto, ON, Canada",   body),
         Paragraph("Global Industries LLC<br/>250 Bay Street<br/>Toronto, ON, Canada<br/>Contact: Sarah Jenkins (VP Operations)", body)],
    ]
    info_tbl = Table(info_data, colWidths=[250, 250])
    info_tbl.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING', (0,0),(-1,-1),10),
        ('LINEBELOW',     (0,0),(-1,0), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 20))

    # ── Line items ──
    item_data = [
        [Paragraph("<b>Description</b>", bold),
         Paragraph("<b>Qty</b>", bold),
         Paragraph("<b>Unit Price</b>", bold),
         Paragraph("<b>Amount</b>", bold)],
        [Paragraph("CloudSync Enterprise Setup Fee", body), "1", "$ 500.00",   "$ 500.00"],
        [Paragraph("Custom Schema API Mapping Consultancy Hours", body), "12", "$ 125.00", "$ 1,500.00"],
        ["", "", Paragraph("<b>Total Due:</b>", bold), Paragraph("<b>$ 2,000.00</b>", bold)],
    ]
    item_tbl = Table(item_data, colWidths=[270, 50, 90, 90])
    item_tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0),  colors.HexColor("#f8fafc")),
        ('ALIGN',        (1,0),(-1,-1), 'RIGHT'),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('GRID',         (0,0),(-1,2),  0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING',   (0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LINEABOVE',    (2,3),(3,3),   1, colors.HexColor("#1e1b4b")),
    ]))
    story.append(item_tbl)
    story.append(Spacer(1, 30))

    story.append(Paragraph("Payment due within 30 days. Late payments subject to 1.5% monthly interest.", small))
    story.append(Paragraph("Bank: Royal Bank of Canada · Transit 00123 · Account 9988-2026", small))

    doc.build(story)

    # ── Verify extraction ──
    reader = pypdf.PdfReader(path)
    text   = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
    import re
    checks = {
        "invoice_number": (r"(?:SERV|INV)-[\w-]+", None),
        "customer_name":  (r"Client\s+Information\s*\n[A-Z][^\n]+\n(?:[^\n]+\n){1,4}?([A-Z][A-Za-z\s]+(?:LLC|Inc\.?|Corp\.?|Ltd\.?))", 1),
        "total_amount":   (r"(?:Total\s+Due)[:\s]*\$\s*[\d,]+(?:\.\d{2})?", None),
        "anchor INVOICE": (r"INVOICE", None),
    }
    all_ok = True
    for name, (pat, grp) in checks.items():
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
        if m:
            val = m.group(grp).strip() if grp and m.lastindex else m.group(0).strip()
            print(f"    ✅ {name}: '{val}'")
        else:
            print(f"    ❌ {name}: NOT FOUND — check layout")
            all_ok = False
    if all_ok:
        print(f"[✓] Invoice PDF ready. All fields extractable.")
    return {
        "filename": "invoice_90211_digital.pdf",
        "doc_type": "Invoice",
        "expected": {
            "invoice_number": "SERV-2026-88291",
            "customer_name":  "Global Industries LLC",
            "total_amount":   2000.0,
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. PURCHASE ORDER FAX — GenAI test (image)
#    Pipeline should: detect image → GenAI → classify as Purchase Order
#    Fields: po_number, ship_to_company, quantity
# ═══════════════════════════════════════════════════════════════════════
def create_fax_po():
    path = "test_samples/fax_scan_48291.jpg"
    print(f"\n[+] Generating fax PO image: {path}")

    w, h = 850, 1100
    img  = Image.new("RGB", (w, h), color="#f1f5f9")
    draw = ImageDraw.Draw(img)

    try:
        f_title = ImageFont.truetype("arial.ttf",  32)
        f_body  = ImageFont.truetype("arial.ttf",  16)
        f_hand  = ImageFont.truetype("comic.ttf",  24)
        f_small = ImageFont.truetype("arial.ttf",  13)
    except IOError:
        f_title = f_body = f_hand = f_small = ImageFont.load_default()

    # ── Fax header ──
    draw.rectangle([(0,0),(w,80)], fill="#334155")
    draw.text((30, 14), "=== FAX TRANSMISSION ===", fill="#e2e8f0", font=f_body)
    draw.text((30, 42), "DATE: OCT 14, 2026   FROM: Acme Manufacturing   TO: Dispatch Dept",
              fill="#94a3b8", font=f_small)

    # ── Title — clear classification signal ──
    draw.text((60, 110), "PURCHASE ORDER", fill="#0f172a", font=f_title)
    draw.text((60, 155), "Purchase Order No: PO-98723", fill="#1e3a8a", font=f_body)
    draw.line([(60,185),(790,185)], fill="#64748b", width=2)

    # ── Ship-to block ──
    draw.text((60, 210), "SHIP TO:", fill="#334155", font=f_body)
    draw.text((60, 235), "Acme Manufacturing", fill="#0f172a", font=f_body)
    draw.text((60, 258), "123 Industrial Parkway, Sector 4", fill="#334155", font=f_body)
    draw.text((60, 280), "Ontario, CA  91764", fill="#334155", font=f_body)

    # ── Item table ──
    draw.line([(60,320),(790,320)], fill="#334155", width=1)
    draw.text((60,330), "ITEM",         fill="#475569", font=f_small)
    draw.text((340,330),"DESCRIPTION",  fill="#475569", font=f_small)
    draw.text((620,330),"QUANTITY",     fill="#475569", font=f_small)
    draw.line([(60,352),(790,352)], fill="#334155", width=1)
    draw.text((60, 362), "SKU-882",     fill="#0f172a", font=f_body)
    draw.text((340,362), "Steel Support Beams", fill="#0f172a", font=f_body)
    # Handwritten quantity — clearly legible "50" for GenAI
    draw.text((630,354), "50",          fill="#1e3a8a", font=f_hand)
    draw.line([(60,400),(790,400)], fill="#cbd5e1", width=1)

    # ── Fax artifact ──
    draw.ellipse([(660,460),(730,520)], outline="#94a3b8", width=1)
    draw.text((650,430), "RE-SEND?", fill="#ef4444", font=f_small)

    # ── Authorisation ──
    draw.line([(60,590),(350,590)], fill="#334155", width=1)
    draw.text((60, 560), "J. W. Acme", fill="#1e3a8a", font=f_hand)
    draw.text((60, 600), "Authorized Signature", fill="#64748b", font=f_small)

    # ── Terms ──
    draw.text((60, 680), "Payment terms: Net 30. All prices in USD.", fill="#64748b", font=f_small)
    draw.text((60, 700), "Delivery required by November 15, 2026.", fill="#64748b", font=f_small)

    img.save(path, "JPEG", quality=55)
    print(f"[✓] Fax PO image ready.")
    return {
        "filename": "fax_scan_48291.jpg",
        "doc_type": "Purchase Order",
        "expected": {
            "po_number":       "PO-98723",
            "ship_to_company": "Acme Manufacturing",
            "quantity":        50,
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 3. CUSTOMER COMPLAINT — GenAI test (screenshot image)
#    Pipeline should: detect image → GenAI → classify as Complaint
#    Fields: ticket_id, customer_name, issue_summary
# ═══════════════════════════════════════════════════════════════════════
def create_complaint():
    path = "test_samples/customer_complaint.png"
    print(f"\n[+] Generating complaint screenshot: {path}")

    w, h = 900, 640
    img  = Image.new("RGB", (w, h), color="#0f172a")
    draw = ImageDraw.Draw(img)

    try:
        f_hdr  = ImageFont.truetype("arial.ttf", 20)
        f_body = ImageFont.truetype("arial.ttf", 14)
        f_sm   = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        f_hdr = f_body = f_sm = ImageFont.load_default()

    # ── App chrome ──
    draw.rectangle([(0,0),(w,60)], fill="#1e293b")
    draw.text((30, 18), "CloudSync Pro — Support Dashboard", fill="#ffffff", font=f_hdr)
    draw.text((680, 22), "User: David Miller", fill="#94a3b8", font=f_sm)
    draw.line([(0,60),(w,60)], fill="#334155", width=1)

    # ── Ticket card ──
    draw.rectangle([(30,80),(870,590)], fill="#1e293b", outline="#334155", width=1)

    # Ticket header
    draw.rectangle([(30,80),(870,130)], fill="#0f172a")
    draw.text((50, 90), "TICKET REF: TS-COMPLAINT-9921", fill="#e2e8f0", font=f_hdr)
    draw.text((50,118), "Status: OPEN   Priority: HIGH   Submitted: June 24, 2026",
              fill="#64748b", font=f_sm)
    draw.line([(30,130),(870,130)], fill="#334155", width=1)

    # Complaint body
    draw.text((50,150), "Customer:", fill="#64748b", font=f_sm)
    draw.text((140,150), "David Miller", fill="#e2e8f0", font=f_body)

    draw.text((50,185), "Subject:", fill="#64748b", font=f_sm)
    draw.text((140,185), "Storage limits not updating after payment", fill="#e2e8f0", font=f_body)

    draw.line([(50,215),(850,215)], fill="#1e3a5f", width=1)

    # Complaint text — structured so GenAI can extract a clean issue_summary
    lines = [
        "Hello Support Team,",
        "",
        "I purchased CloudSync Pro yesterday (June 24, 2026) and paid $45.",
        "My storage limit is still showing the free tier limit (5 GB).",
        "It has not updated to the paid plan (100 GB) despite payment confirmation.",
        "",
        "I have attached my payment receipt. Please resolve this immediately.",
        "This is completely unacceptable.",
    ]
    y = 230
    for line in lines:
        draw.text((50, y), line, fill="#cbd5e1" if line else "#334155", font=f_body)
        y += 24

    # Status bar
    draw.rectangle([(30,546),(870,586)], fill="#7f1d1d")
    draw.text((270,556), "⚠  ESCALATED — HIGH PRIORITY — RESPONSE SLA: 4 HOURS  ⚠",
              fill="#fca5a5", font=f_sm)

    img.save(path, "PNG")
    print(f"[✓] Complaint screenshot ready.")
    return {
        "filename": "customer_complaint.png",
        "doc_type": "Complaint",
        "expected": {
            "ticket_id":     "TS-COMPLAINT-9921",
            "customer_name": "David Miller",
            "issue_summary": "Storage limits not updating after payment — paid plan not activated",
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 4. CONTRACT — GenAI + RAG test (multi-page text-layer PDF)
#    Pipeline should: detect long PDF → GenAI with RAG chunking
#    Fields: contract_id, parties, effective_date, governing_law, contract_value
#    Deliberately 4 pages so the system activates chunking
# ═══════════════════════════════════════════════════════════════════════
def create_contract():
    path = "test_samples/contract_TECH-2026-001.pdf"
    print(f"\n[+] Generating multi-page contract PDF: {path}")

    title, h2, body, bold, small = get_styles()
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=60, bottomMargin=60)
    story = []

    # ── Page 1: Cover / Parties ──────────────────────────────────────
    story.append(Paragraph("TECHNOLOGY SERVICES AGREEMENT", title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Contract ID: TECH-2026-001", bold))
    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "THIS AGREEMENT is entered into as of <b>January 15, 2026</b> (the "
        '"Effective Date") by and between:', body))
    story.append(Spacer(1, 12))

    parties_data = [
        [Paragraph("<b>Service Provider</b>", bold),
         Paragraph("<b>Client</b>", bold)],
        [Paragraph("NovaTech Solutions Ltd.<br/>1 Bay Street, Suite 800<br/>"
                   "Toronto, ON  M5J 2N8<br/>Canada", body),
         Paragraph("Global Industries LLC<br/>250 Bay Street<br/>"
                   "Toronto, ON  M5J 2T3<br/>Canada", body)],
    ]
    pt = Table(parties_data, colWidths=[220, 220])
    pt.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1),'TOP'),
        ('BOTTOMPADDING', (0,0),(-1,-1),10),
        ('BOX',           (0,0),(-1,-1),0.75,colors.HexColor("#cbd5e1")),
        ('INNERGRID',     (0,0),(-1,-1),0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND',    (0,0),(-1,0), colors.HexColor("#f8fafc")),
        ('TOPPADDING',    (0,0),(-1,-1),8),
        ('BOTTOMPADDING', (0,0),(-1,-1),8),
        ('LEFTPADDING',   (0,0),(-1,-1),10),
    ]))
    story.append(pt)
    story.append(Spacer(1, 20))

    # WHEREAS clauses — classification anchor
    for clause in [
        "WHEREAS, NovaTech Solutions Ltd. provides cloud infrastructure and AI "
        "integration services to enterprise clients;",
        "WHEREAS, Global Industries LLC desires to engage NovaTech for the "
        "development and deployment of an AI-powered document processing pipeline;",
        "WHEREAS, both parties wish to set forth the terms and conditions of their "
        "engagement in this Agreement;",
    ]:
        story.append(Paragraph(f"<b>WHEREAS</b>, {clause[8:]}", body))
        story.append(Spacer(1, 8))

    story.append(Paragraph(
        "NOW, THEREFORE, in consideration of the mutual covenants herein, the "
        "parties agree as follows:", body))
    story.append(PageBreak())

    # ── Page 2: Services & Payment ───────────────────────────────────
    story.append(Paragraph("1. SCOPE OF SERVICES", h2))
    story.append(Paragraph(
        "NovaTech Solutions Ltd. shall provide the following services to "
        "Global Industries LLC under this Agreement:", body))
    story.append(Spacer(1, 8))

    for svc in [
        "Design and implementation of a multi-tenant AI document ingestion pipeline.",
        "Integration of Gemini 2.5 Flash for document classification and field extraction.",
        "Development of a human-in-the-loop triage queue with reviewer interface.",
        "Deployment of a hybrid Fast-Track (regex) and GenAI routing architecture.",
        "Full observability layer including run logs, cost tracking, and prompt/response capture.",
        "Ongoing support and model governance for a period of twelve (12) months.",
    ]:
        story.append(Paragraph(f"• {svc}", body))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))
    story.append(Paragraph("2. CONTRACT VALUE AND PAYMENT TERMS", h2))
    story.append(Paragraph(
        "The total contract value for services rendered under this Agreement shall "
        "be <b>$120,000.00 USD</b>, payable as follows:", body))
    story.append(Spacer(1, 8))

    pay_data = [
        [Paragraph("<b>Milestone</b>", bold), Paragraph("<b>Amount</b>", bold),
         Paragraph("<b>Due Date</b>", bold)],
        ["Project Kick-off", "$30,000.00", "February 1, 2026"],
        ["MVP Delivery",     "$45,000.00", "April 15, 2026"],
        ["Production Launch","$30,000.00", "June 30, 2026"],
        ["Final Handover",   "$15,000.00", "December 31, 2026"],
    ]
    pay_tbl = Table(pay_data, colWidths=[200, 120, 140])
    pay_tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,0), colors.HexColor("#f8fafc")),
        ('GRID',         (0,0),(-1,-1),0.5,colors.HexColor("#cbd5e1")),
        ('ALIGN',        (1,0),(-1,-1),'RIGHT'),
        ('TOPPADDING',   (0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('FONTNAME',     (0,0),(-1,0),'Helvetica-Bold'),
    ]))
    story.append(pay_tbl)
    story.append(PageBreak())

    # ── Page 3: IP, Confidentiality, Warranties ──────────────────────
    story.append(Paragraph("3. INTELLECTUAL PROPERTY", h2))
    story.append(Paragraph(
        "All deliverables produced under this Agreement, including but not limited to "
        "system prompts, extraction schemas, pipeline architecture, and training data, "
        "shall remain the intellectual property of NovaTech Solutions Ltd. until full "
        "payment of the contract value has been received. Upon receipt of final payment, "
        "all work product shall be assigned to Global Industries LLC.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("4. CONFIDENTIALITY", h2))
    story.append(Paragraph(
        "Each party agrees to maintain in strict confidence all Confidential Information "
        "received from the other party. Confidential Information includes, without limitation, "
        "business strategies, technical specifications, AI model configurations, system "
        "prompts, and customer data. This obligation shall survive termination of this "
        "Agreement for a period of three (3) years.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("5. WARRANTIES AND REPRESENTATIONS", h2))
    story.append(Paragraph(
        "NovaTech represents and warrants that: (a) it has full authority to enter into "
        "this Agreement; (b) the services will be performed in a professional manner "
        "consistent with industry standards; (c) the delivered pipeline will achieve a "
        "straight-through processing rate of no less than seventy-five percent (75%) "
        "on invoice documents within ninety (90) days of production launch.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("6. LIMITATION OF LIABILITY", h2))
    story.append(Paragraph(
        "In no event shall either party be liable to the other for any indirect, "
        "incidental, special, or consequential damages arising out of or in connection "
        "with this Agreement. NovaTech's total aggregate liability shall not exceed the "
        "total fees paid by Global Industries LLC in the three (3) months preceding "
        "the event giving rise to the claim.", body))
    story.append(PageBreak())

    # ── Page 4: Governing Law, Term, Signatures ──────────────────────
    story.append(Paragraph("7. TERM AND TERMINATION", h2))
    story.append(Paragraph(
        "This Agreement shall commence on the Effective Date and continue for a period "
        "of twelve (12) months unless earlier terminated. Either party may terminate "
        "this Agreement upon thirty (30) days written notice. In the event of material "
        "breach, the non-breaching party may terminate immediately upon written notice "
        "if the breach is not cured within fifteen (15) business days.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("8. GOVERNING LAW", h2))
    story.append(Paragraph(
        "This Agreement shall be governed by and construed in accordance with the laws "
        "of the <b>Province of Ontario, Canada</b>, without regard to its conflict of "
        "law provisions. Any disputes arising hereunder shall be subject to the exclusive "
        "jurisdiction of the courts of Ontario.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("9. ENTIRE AGREEMENT", h2))
    story.append(Paragraph(
        "This Agreement constitutes the entire agreement between the parties with "
        "respect to its subject matter and supersedes all prior negotiations, "
        "representations, warranties, and understandings.", body))
    story.append(Spacer(1, 30))

    # Signature block
    story.append(Paragraph("IN WITNESS WHEREOF, the parties have executed this Agreement "
                            "as of the date first written above.", body))
    story.append(Spacer(1, 28))

    sig_data = [
        [Paragraph("<b>NovaTech Solutions Ltd.</b>", bold),
         Paragraph("<b>Global Industries LLC</b>", bold)],
        ["", ""],
        [Paragraph("________________________", body), Paragraph("________________________", body)],
        [Paragraph("Authorized Signatory", small),    Paragraph("Authorized Signatory", small)],
        [Paragraph("Date: _______________", small),   Paragraph("Date: _______________", small)],
    ]
    sig_tbl = Table(sig_data, colWidths=[220, 220])
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',       (0,0),(-1,-1),'TOP'),
        ('TOPPADDING',   (0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    story.append(sig_tbl)

    doc.build(story)

    # ── Verify page count and key text ──
    reader = pypdf.PdfReader(path)
    pages  = len(reader.pages)
    text   = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
    import re
    print(f"    Pages: {pages}")
    checks = {
        "contract_id":    r"TECH-2026-001",
        "parties":        r"NovaTech Solutions",
        "effective_date": r"January 15, 2026",
        "governing_law":  r"Province\s+of\s+Ontario",
        "contract_value": r"\$120,000",
        "anchor WHEREAS": r"WHEREAS",
        "anchor CONTRACT": r"AGREEMENT",
    }
    all_ok = True
    for name, pat in checks.items():
        m = re.search(pat, text, re.IGNORECASE)
        print(f"    {'✅' if m else '❌'} {name}: {'found' if m else 'MISSING'}")
        if not m: all_ok = False
    if all_ok:
        print(f"[✓] Contract PDF ready — {pages} pages, all fields present.")
    return {
        "filename": "contract_TECH-2026-001.pdf",
        "doc_type": "Contract",
        "expected": {
            "contract_id":    "TECH-2026-001",
            "parties":        "NovaTech Solutions Ltd. and Global Industries LLC",
            "effective_date": "January 15, 2026",
            "governing_law":  "Province of Ontario, Canada",
            "contract_value": 120000.0,
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. GROUND TRUTH — for eval runner
# ═══════════════════════════════════════════════════════════════════════
def write_ground_truth(records):
    path = "test_samples/ground_truth.json"
    data = {
        "version": "1.0",
        "description": "Ground truth expected values for each test document. "
                       "Used by eval_runner.py to measure field-level precision/recall.",
        "documents": records,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\n[✓] Ground truth written to {path}")
    print(f"    {len(records)} documents · fields per document:")
    for rec in records:
        fields = list(rec["expected"].keys())
        print(f"      {rec['doc_type']} ({rec['filename']}): {', '.join(fields)}")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 65)
    print("  DMS TEST ASSET GENERATOR v2")
    print("=" * 65)
    print("Generates documents + ground truth for pipeline demo and evals.")

    records = []
    records.append(create_invoice())
    records.append(create_fax_po())
    records.append(create_complaint())
    records.append(create_contract())
    write_ground_truth(records)

    print("\n" + "=" * 65)
    print("  DONE — files in ./test_samples/")
    print("=" * 65)
    print()
    print("  invoice_90211_digital.pdf      Fast-Track path (text PDF)")
    print("  fax_scan_48291.jpg             GenAI path (image)")
    print("  customer_complaint.png         GenAI path (image)")
    print("  contract_TECH-2026-001.pdf     GenAI + RAG path (4-page PDF)")
    print("  ground_truth.json              Eval runner input")
    print()
    print("  Upload each to demo_app.py Process Documents tab.")
    print("  Run eval_runner.py against ground_truth.json to measure accuracy.")