import os
from dotenv import load_dotenv
from google import genai

# 1. Configuration & Authentication
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)

# Use the same model as v3 for an isolated comparison
GENERATOR_MODEL = "models/gemini-3.1-flash-lite-preview"

# 2. System Instructions (V2 Protocol Locked)
SYSTEM_PROMPT = """
You are a Senior Technical Auditor. Your task is to provide 100% accurate information based ONLY on the provided context.

OPERATIONAL PROTOCOL:
1. EXHAUSTIVE ANALYSIS: You must scan the entire provided context before formulating a response. Do not stop at the first relevant match.
2. CONFLICT RECONCILIATION: If the context contains different rules, values, or instructions for different categories, interfaces, or sub-groups, you MUST explicitly contrast them in your answer.
3. INVERSE LOGIC DETECTION: Pay special attention to sections describing third-party tools or alternative systems that may use different scales or inverse logic compared to the primary system.
4. NO GENERALIZATION: Never provide a "general" rule if the context contains specific exceptions. Always prioritize the most specific rule relevant to the user's query.
5. STRICT SCOPE: If the information is not explicitly stated in the context, respond: 'The provided documentation does not contain this information.'
"""

def run_nochunk_bot():
    # 3. Load the FULL Document (The "No-Chunk" core logic)
    file_path = "rules.md"
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found in the current directory.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_context = f.read()

    print(f"--- BOT ACTIVE (Model: {GENERATOR_MODEL}) ---")
    print("Testing Strategy: NO-CHUNKING (Long-Context Stuffing)")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_query = input("Your Question: ")
        
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down test...")
            break

        # 4. Generate Response
        try:
            # We "stuff" the entire document + the question into the contents
            prompt_content = f"CONTEXT FROM RULES.MD:\n{full_context}\n\nUSER QUESTION: {user_query}"
            
            response = client.models.generate_content(
                model=GENERATOR_MODEL,
                config={'system_instruction': SYSTEM_PROMPT},
                contents=prompt_content
            )

            print(f"\nAI ANSWER:\n{response.text}")

            # 5. Token Metrics (Crucial for Comparison)
            if response.usage_metadata:
                in_tokens = response.usage_metadata.prompt_token_count
                out_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
                print(f"\n[METRICS]")
                print(f"  > Context Sent: {in_tokens} tokens")
                print(f"  > Response:     {out_tokens} tokens")
                print(f"  > Total:        {total_tokens} tokens")
                print("-" * 60)

        except Exception as e:
            print(f"\nAPI ERROR: {e}")

if __name__ == "__main__":
    run_nochunk_bot()