import os
import time
import math
from dotenv import load_dotenv
from google import genai

# ==========================================
# 0. SETUP & VISUALS
# ==========================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ==========================================
# 1. OBSERVABILITY LOGGING
# ==========================================
def track_llm_call(agent_name, prompt, color):
    """Wraps text generation calls for observability."""
    print(f"│\n▼\n{color}{Colors.BOLD}[{agent_name}]{Colors.RESET}")
    print(f" ├─ {Colors.BLUE}Status:{Colors.RESET} Generating...")
    
    start = time.time()
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    latency = round(time.time() - start, 2)
    
    tokens_in = response.usage_metadata.prompt_token_count
    tokens_out = response.usage_metadata.candidates_token_count
    
    print(f"\033[F\033[K ├─ ⏱️  {Colors.BLUE}Latency:{Colors.RESET} {latency}s")
    print(f" ├─ 🪙  {Colors.BLUE}Tokens:{Colors.RESET} {tokens_in} in | {tokens_out} out")
    
    return response.text.strip()

def track_embedding_call(text):
    """Wraps embedding calls for observability."""
    start = time.time()
    
    # UPDATE THIS LINE:
    response = client.models.embed_content(model="gemini-embedding-001", contents=text)
    
    latency = round(time.time() - start, 2)
    
    # The API returns a list of embeddings. We want the vector array from the first one.
    vector = response.embeddings[0].values
    return vector, latency

# ==========================================
# 2. IN-MEMORY VECTOR STORE (RAG)
# ==========================================
class SimpleVectorStore:
    def __init__(self):
        self.chunks = []
        self.vectors = []

    def add_chunk(self, text):
        vector, latency = track_embedding_call(text)
        self.chunks.append(text)
        self.vectors.append(vector)
        return latency

    def search(self, query_text, top_k=1):
        """Finds the most mathematically similar chunk using Cosine Similarity."""
        query_vector, latency = track_embedding_call(query_text)
        
        scores = []
        for i, doc_vector in enumerate(self.vectors):
            # Pure Python Cosine Similarity Math
            dot_product = sum(a * b for a, b in zip(query_vector, doc_vector))
            mag_a = math.sqrt(sum(a * a for a in query_vector))
            mag_b = math.sqrt(sum(b * b for b in doc_vector))
            similarity = dot_product / (mag_a * mag_b) if mag_a and mag_b else 0
            scores.append((similarity, self.chunks[i]))
            
        # Sort by highest score and return top results
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k], latency

# ==========================================
# 3. INITIALIZING THE KNOWLEDGE BASE
# ==========================================
print(f"{Colors.BOLD}⚙️ INITIALIZING VECTOR DATABASE...{Colors.RESET}")
db = SimpleVectorStore()

raw_documents = [
    "To reset your password, navigate to Settings > Security > Reset Password.",
    "Standard shipping takes 3-5 business days. Expedited takes 1-2 days.",
    "Refunds are only issued for unopened items returned within 30 days."
]

total_latency = 0
for i, doc in enumerate(raw_documents):
    lat = db.add_chunk(doc)
    total_latency += lat
    print(f" └─ Embedded Chunk {i+1}/3 [{lat}s]")
print(f"{Colors.GREEN}Database ready in {round(total_latency, 2)}s.{Colors.RESET}\n")

# ==========================================
# 4. THE ORCHESTRATOR LOGIC
# ==========================================
def process_user_query(query):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"👤 {Colors.CYAN}{Colors.BOLD}USER INPUT:{Colors.RESET} {query}")

    # --- STEP 1: The Router Agent ---
    router_prompt = f'Categorize message. If simple/policy, reply "KB". If angry/exception, reply "ESCALATE".\nMsg: {query}'
    route_decision = track_llm_call("ROUTER AGENT", router_prompt, Colors.YELLOW).upper()
    print(f" └─ 🔀 {Colors.BLUE}Decision:{Colors.RESET} {route_decision}")
    
    # --- STEP 2: The Branching Logic ---
    if "KB" in route_decision:
        print(f"│\n▼\n{Colors.GREEN}{Colors.BOLD}[VECTOR DATABASE]{Colors.RESET}")
        print(f" ├─ {Colors.BLUE}Status:{Colors.RESET} Performing Semantic Search...")
        
        results, search_lat = db.search(query, top_k=1)
        best_chunk = results[0][1]
        confidence = round(results[0][0] * 100, 1)
        
        print(f"\033[F\033[K ├─ ⏱️  {Colors.BLUE}Latency:{Colors.RESET} {search_lat}s")
        print(f" ├─ 🎯 {Colors.BLUE}Match Confidence:{Colors.RESET} {confidence}%")
        print(f" └─ 📄 {Colors.BLUE}Retrieved Chunk:{Colors.RESET} '{best_chunk}'")
        
        # The KB Worker Agent
        kb_prompt = f"Answer using ONLY this fact: '{best_chunk}'. Query: {query}"
        response = track_llm_call("KB SUPPORT AGENT", kb_prompt, Colors.GREEN)
        print(f" └─ 📝 {Colors.BLUE}Action:{Colors.RESET} Drafted Context-Aware Response")
        
        print(f"│\n▼\n✅ {Colors.GREEN}{Colors.BOLD}FINAL OUTPUT TO USER:{Colors.RESET}")
        print(f"   {response}\n")

    else:
        # The Escalation Worker Agent
        escalation_prompt = f"Draft 2-sentence internal summary of this angry message. Label urgency.\nMsg: {query}"
        ticket_summary = track_llm_call("ESCALATION AGENT", escalation_prompt, Colors.RED)
        print(f" └─ 📝 {Colors.BLUE}Action:{Colors.RESET} Drafted Human Hand-off Ticket")
        
        print(f"│\n▼\n✉️  {Colors.MAGENTA}{Colors.BOLD}TICKET ROUTED TO HUMAN:{Colors.RESET}")
        print(f"   {ticket_summary}")
        
        print(f"\n✅ {Colors.GREEN}{Colors.BOLD}FINAL OUTPUT TO USER:{Colors.RESET}")
        print(f"   I have escalated this to our human support team. They will email you shortly.\n")

# ==========================================
# 5. INTERACTIVE CHAT LOOP
# ==========================================
if __name__ == "__main__":
    print(f"{Colors.BOLD}🚀 STARTING RAG ORCHESTRATOR DEMO{Colors.RESET}")
    print(f"Type 'exit' to end.\n")
    
    while True:
        user_input = input(f"👤 {Colors.CYAN}[You]:{Colors.RESET} ")
        if user_input.strip().lower() in ['exit', 'quit']:
            break
        if user_input.strip():
            process_user_query(user_input)