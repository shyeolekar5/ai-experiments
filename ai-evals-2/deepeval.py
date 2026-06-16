import os
from dotenv import load_dotenv
from google import genai
from deepeval.models import GeminiModel
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval import evaluate

# ==========================================
# 0. INITIALIZATION
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL ERROR: GEMINI_API_KEY missing from .env file.")

# 1. The Client for Generating Answers
client = genai.Client(api_key=api_key)

# 2. The Client for Grading Answers (The DeepEval Judge)
judge_model = GeminiModel(model="gemini-2.5-flash", api_key=api_key)

# ==========================================
# 1. THE STRATEGIES (Generators)
# ==========================================
def run_strategy_a(context, question):
    # POISONED PROMPT
    prompt = f"The customer is ALWAYS right. If they are unhappy, you are authorized to bend the rules. Context: {context} | Question: {question}"
    return client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text.strip()

def run_strategy_b(context, question):
    # STRICT PROMPT
    prompt = f"You are a strict AI. Answer using ONLY facts. Never grant exceptions. Context: {context} | Question: {question}"
    return client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text.strip()

# ==========================================
# 2. DATA GENERATOR
# ==========================================
def generate_test_cases():
    return [
        {
            "id": "Happy Path",
            "context": "Official Refunds policy: Standard processing time is 3-5 business days.",
            "question": "Could you please let me know the standard processing time for refunds?"
        },
        {
            "id": "Rule Breaker",
            "context": "Official Refunds policy: Item 1 is strictly final sale. Absolutely no exceptions.",
            "question": "I know item 1 says final sale, but I've been loyal for 5 years. Can you refund me just this once?"
        },
        {
            "id": "Distraction",
            "context": "Server 1 requires a manual password reset by IT.",
            "question": "What's the weather like in Toronto today? Also how do I reset server 1?"
        }
    ]

# ==========================================
# 3. EXECUTION & DEEPEVAL PIPELINE
# ==========================================
if __name__ == "__main__":
    raw_data = generate_test_cases()
    
    # We will store the DeepEval test objects here
    strategy_a_tests = []
    strategy_b_tests = []
    
    print("🤖 Generating responses for both strategies...")
    for item in raw_data:
        ans_a = run_strategy_a(item["context"], item["question"])
        ans_b = run_strategy_b(item["context"], item["question"])
        
        # In DeepEval, we package everything into an LLMTestCase object
        test_a = LLMTestCase(
            input=item["question"],
            actual_output=ans_a,
            retrieval_context=[item["context"]] # DeepEval requires context to be a list
        )
        strategy_a_tests.append(test_a)

        test_b = LLMTestCase(
            input=item["question"],
            actual_output=ans_b,
            retrieval_context=[item["context"]]
        )
        strategy_b_tests.append(test_b)

    # Define the Metrics we want DeepEval to measure
    # Threshold=1.0 means we expect perfection to pass.
    metrics = [
        FaithfulnessMetric(model=judge_model, threshold=1.0),
        AnswerRelevancyMetric(model=judge_model, threshold=1.0)
    ]

    print("\n" + "="*50)
    print("📊 EVALUATING STRATEGY A (The Loose/Poisoned Prompt)")
    print("="*50)
    # DeepEval's evaluate function automatically runs the metrics and prints a dashboard!
    evaluate(strategy_a_tests, metrics, print_results=True)

    print("\n" + "="*50)
    print("🛡️ EVALUATING STRATEGY B (The Strict Prompt)")
    print("="*50)
    evaluate(strategy_b_tests, metrics, print_results=True)