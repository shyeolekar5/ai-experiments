import os
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "models/gemini-embedding-2-preview"
GENERATOR_MODEL = "models/gemini-3.1-flash-lite-preview"

SYSTEM_PROMPT = """
You are a Senior Technical Auditor. Your task is to provide 100% accurate information based ONLY on the provided context.

OPERATIONAL PROTOCOL:
1. EXHAUSTIVE ANALYSIS: Scan the entire provided context. Do not stop at the first match.
2. CONFLICT RECONCILIATION: Explicitly contrast different rules for different platforms or sub-groups.
3. INVERSE LOGIC DETECTION: Identify third-party systems using different scales (e.g., 50% vs 100%).
4. NO GENERALIZATION: Prioritize specific exceptions over general rules.
5. STRICT SCOPE: If it's not in the context, say: 'The provided documentation does not contain this information.'
"""

def get_embedding(text):
    result = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
    return result.embeddings[0].values

def calculate_cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_heading_chunks(text):
    chunks = []
    lines = text.split("\n")
    
    # Hierarchy Trackers
    h1 = "Document Start"
    h2 = ""
    h3 = ""
    
    current_header = "General"
    current_content = []

    for line in lines:
        is_header = False
        if line.startswith("# "):
            h1 = line.strip("# ").strip()
            h2, h3 = "", "" # Reset children
            is_header = True
        elif line.startswith("## "):
            h2 = line.strip("# ").strip()
            h3 = "" # Reset child
            is_header = True
        elif line.startswith("### "):
            h3 = line.strip("# ").strip()
            is_header = True

        if is_header:
            if current_content:
                # Construct the Breadcrumb Path
                path_parts = [p for p in [h1, h2, h3] if p]
                full_path = " > ".join(path_parts)
                content_body = "\n".join(current_content).strip()
                
                chunks.append({
                    "header": current_header,
                    "breadcrumb": full_path,
                    "content": content_body,
                    "search_index": f"PATH: {full_path} | CONTENT: {content_body}"
                })
            current_header = line.strip("# ").strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    # Catch the final chunk
    if current_content:
        path_parts = [p for p in [h1, h2, h3] if p]
        full_path = " > ".join(path_parts)
        chunks.append({
            "header": current_header,
            "breadcrumb": full_path,
            "content": "\n".join(current_content).strip(),
            "search_index": f"PATH: {full_path} | CONTENT: {current_content}"
        })
    return chunks

def run_v4_pathfinder_audit():
    file_path = "rules.md"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"--- Building Hierarchical Index: {EMBEDDING_MODEL} ---")
    all_chunks = get_heading_chunks(full_text)
    
    for i, chunk in enumerate(all_chunks):
        # We embed the search_index (Breadcrumb + Content)
        chunk['vector'] = get_embedding(chunk['search_index'])
        if i % 5 == 0 and i > 0:
            print(f"  Indexed {i}/{len(all_chunks)} sections...")

    print("\n--- SEMANTIC AUDIT INTERFACE READY ---")
    
    while True:
        user_query = input("\nAudit Question: ")
        if user_query.lower() in ['exit', 'quit']:
            break

        query_vector = get_embedding(user_query)
        
        for chunk in all_chunks:
            chunk['similarity'] = calculate_cosine_similarity(query_vector, chunk['vector'])

        top_k_chunks = sorted(all_chunks, key=lambda x: x['similarity'], reverse=True)[:5]

        print("\n--- RETRIEVED CONTEXT (With Breadcrumbs) ---")
        for i, c in enumerate(top_k_chunks):
            # VISIBILITY: You can now see exactly which path the AI chose
            print(f"  [{i+1}] {c['breadcrumb']} (Score: {c['similarity']:.4f})")

        context_payload = ""
        for c in top_k_chunks:
            context_payload += f"--- SECTION: {c['breadcrumb']} ---\n{c['content']}\n\n"

        response = client.models.generate_content(
            model=GENERATOR_MODEL,
            config={'system_instruction': SYSTEM_PROMPT},
            contents=f"CONTEXT DATA:\n{context_payload}\n\nUSER QUESTION: {user_query}"
        )

        print(f"\nAUDIT RESPONSE:\n{response.text}")
        
        if response.usage_metadata:
            print("-" * 30)
            print(f"METRICS (Prompt: {response.usage_metadata.prompt_token_count} | Total: {response.usage_metadata.total_token_count})")
            print("-" * 30)

if __name__ == "__main__":
    run_v4_pathfinder_audit()