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
1. EXHAUSTIVE ANALYSIS: You must scan the entire provided context before formulating a response. Do not stop at the first relevant match.
2. CONFLICT RECONCILIATION: If the context contains different rules, values, or instructions for different categories, interfaces, or sub-groups, you MUST explicitly contrast them in your answer.
3. INVERSE LOGIC DETECTION: Pay special attention to sections describing third-party tools or alternative systems that may use different scales or inverse logic compared to the primary system.
4. NO GENERALIZATION: Never provide a 'general' rule if the context contains specific exceptions. Always prioritize the most specific rule relevant to the user's query.
5. STRICT SCOPE: If the information is not explicitly stated in the context, respond: 'The provided documentation does not contain this information.'
"""

def get_embedding(text):
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return result.embeddings[0].values

def calculate_cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_heading_chunks(text):
    chunks = []
    lines = text.split("\n")
    current_header = "General Information"
    current_content = []

    for line in lines:
        if line.startswith("## ") or line.startswith("### "):
            if current_content:
                chunks.append({
                    "header": current_header,
                    "content": "\n".join(current_content).strip()
                })
            current_header = line.strip("# ").strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    if current_content:
        chunks.append({
            "header": current_header, 
            "content": "\n".join(current_content).strip()
        })
    return chunks

def run_v3_semantic_audit():
    file_path = "rules.md"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"--- Building Index: {EMBEDDING_MODEL} ---")
    all_chunks = get_heading_chunks(full_text)
    
    for i, chunk in enumerate(all_chunks):
        chunk['vector'] = get_embedding(chunk['content'])
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

        print("\n--- RETRIEVED CONTEXT CHUNKS ---")
        for i, c in enumerate(top_k_chunks):
            print(f"  [{i+1}] Section: {c['header']} | Score: {c['similarity']:.4f}")

        context_payload = ""
        for c in top_k_chunks:
            context_payload += f"--- SECTION: {c['header']} ---\n{c['content']}\n\n"

        response = client.models.generate_content(
            model=GENERATOR_MODEL,
            config={'system_instruction': SYSTEM_PROMPT},
            contents=f"CONTEXT DATA:\n{context_payload}\n\nUSER QUESTION: {user_query}"
        )

        print(f"\nAUDIT RESPONSE:\n{response.text}")
        
        if response.usage_metadata:
            print("-" * 30)
            print(f"METRICS")
            print(f"  > Model: {GENERATOR_MODEL}")
            print(f"  > Prompt Tokens: {response.usage_metadata.prompt_token_count}")
            print(f"  > Total Tokens:  {response.usage_metadata.total_token_count}")
            print("-" * 30)

if __name__ == "__main__":
    run_v3_semantic_audit()