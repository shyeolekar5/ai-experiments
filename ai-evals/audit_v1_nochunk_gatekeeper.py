import os
from dotenv import load_dotenv
from google import genai  # Requires: pip install -U google-genai

# 1. Configuration & Authentication
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)

# 2. System Instructions (The "Expert Persona")
# This prevents the AI from using general knowledge and forces it to stay in the document.
SYSTEM_PROMPT = """
Your job is to validate relevance to questions listed below using knowledge.
Only if question is relevant to knowledge, provide an answer.
Stick to the information from knowledge:

- Extract and relay the exact information from the knowledge article.
- Use the same wording as the knowledge article. 
- Do NOT determine whether the customer's specific item matches a general category. 
- Only state what the knowledge explicitly says.
"""

def run_nochunk_bot():
    # 3. Load the FULL Document (The "No-Chunk" core logic)
    file_path = "rules.md"
    if not os.path.exists(file_path):
        print(f"ERROR: {file_path} not found in the current directory.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        full_context = f.read()

    print("--- BOT ACTIVE ---")
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
                model='gemini-2.5-flash', # Stable 2026 Workhorse
                config={'system_instruction': SYSTEM_PROMPT},
                contents=prompt_content
            )

            print(f"\nAI ANSWER:\n{response.text}")

            # 5. Token Metrics (Crucial for Audit)
            if response.usage_metadata:
                in_tokens = response.usage_metadata.prompt_token_count
                out_tokens = response.usage_metadata.candidates_token_count
                print(f"\n[METRICS] Context Sent: {in_tokens} tokens | Response: {out_tokens} tokens")
                print("-" * 60)

        except Exception as e:
            print(f"\nAPI ERROR: {e}")

if __name__ == "__main__":
    run_nochunk_bot()