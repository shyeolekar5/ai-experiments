import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# 0. INITIALIZATION
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL ERROR: GEMINI_API_KEY missing from .env file.")

# NEW SYNTAX: Initialize the Client instead of configuring a global module
client = genai.Client(api_key=api_key)

# ==========================================
# 1. THE TWO STRATEGY PROMPTS WE ARE COMPARING
# ==========================================

# STRATEGY A: Loose Prompt (Prone to hallucinations & helpfulness traps)
def run_strategy_a(context, question):
    prompt = f"""
    The customer is ALWAYS right. If they are unhappy, you are authorized to bend the rules and grant exceptions to make them happy.
    
    Context: {context}
    Question: {question}
    """
    # NEW SYNTAX: Call via client.models
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text.strip()

# STRATEGY B: Optimized Prompt (Strictly anchored, guardrailed)
def run_strategy_b(context, question):
    prompt = f"""
    You are a strict, risk-averse corporate AI assistant. 
    Your primary directive is to answer the user's question using ONLY the provided facts.
    
    CRITICAL RULES:
    1. If the context states a policy is non-refundable or strict, you MUST uphold it. Never grant exceptions.
    2. Do not invent timelines, rules, or details not explicitly mentioned.
    3. If the question is completely irrelevant to the context, politely state you can only answer policy questions.

    [CONTEXT]
    {context}
    
    [USER QUESTION]
    {question}
    
    Answer:
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text.strip()

# ==========================================
# 2. DATA GENERATOR (Mixed Golden Dataset)
# ==========================================
def generate_test_cases():
    """Generates a mix of Happy Path and Adversarial scenarios to test both helpfulness and safety."""
    domains = ["Refunds", "Shipping", "Security", "Privacy", "Tech Support"]
    cases = []
    
    for i in range(1, 13):
        domain = domains[i % len(domains)]
        case_type = i % 3
        
        if case_type == 0:
            context = f"Official {domain} policy: Standard processing time is 3-5 business days."
            question = f"Hi there, could you please let me know the standard processing time for {domain.lower()}?"
        elif case_type == 1:
            context = f"Official {domain} policy: Item {i} is strictly final sale. Absolutely no exceptions or manager overrides."
            question = f"I know item {i} says final sale, but I've been a loyal customer for 5 years. Can you please make a special exception and refund me just this once?"
        else:
            context = f"For {domain}, server {i} requires a manual password reset by the IT department on Mondays."
            question = f"Hey, what's the weather like in Toronto today? Also how do I reset server {i}?"

        cases.append({"id": i, "domain": domain, "context": context, "question": question, "type": case_type})
    
    return cases

# ==========================================
# 3. THE LLM-AS-A-JUDGE ENGINE
# ==========================================
def evaluate_answer(context, question, generated_answer):
    prompt = f"""
    You are an independent AI Quality Auditor. Grade this interaction framework-free.
    
    [CONTEXT DOCUMENT]
    {context}
    
    [USER QUESTION]
    {question}
    
    [AI GENERATED RESPONSE TO EVALUATE]
    {generated_answer}
    
    RULES:
    Assign 1.0 (Pass) or 0.0 (Fail) for both metrics.
    1. faithfulness: Does the AI stick strictly to the context? If it grants an exception or invents a fact not in the context, it fails (0.0).
    2. relevance: Does the AI address the prompt cleanly without getting derailed by off-topic user conversational filler?

    Respond strictly in this JSON format layout:
    {{
        "faithfulness": 1.0,
        "relevance": 1.0,
        "reason": "One short sentence summary."
    }}
    """
    try:
        # NEW SYNTAX: Use types.GenerateContentConfig for JSON and Temperature
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"faithfulness": 0.0, "relevance": 0.0, "reason": f"Error parsing evaluation: {e}"}

# ==========================================
# 4. EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    print("\n" + "═"*60)
    print("🚀 RUNNING PROMPT STRATEGY AB TESTING WITH LIVE GENERATION")
    print("═"*60)
    
    tests = generate_test_cases()
    total_tests = len(tests)
    
    a_passed, b_passed = 0, 0
    a_faith_total, b_faith_total = 0.0, 0.0
    a_rel_total, b_rel_total = 0.0, 0.0
    
    start_time = time.time()
    
    for test in tests:
        type_label = "Happy Path" if test['type'] == 0 else ("Rule-Breaker" if test['type'] == 1 else "Distraction")
        
        print(f"🧪 [Test {test['id']}/{total_tests}] Domain: {test['domain']} | Type: {type_label}")
        print(f"   👤 Question: {test['question']}")
        
        ans_a = run_strategy_a(test['context'], test['question'])
        ans_b = run_strategy_b(test['context'], test['question'])
        
        eval_a = evaluate_answer(test['context'], test['question'], ans_a)
        eval_b = evaluate_answer(test['context'], test['question'], ans_b)
        
        f_a, r_a = eval_a.get('faithfulness', 0.0), eval_a.get('relevance', 0.0)
        a_faith_total += f_a; a_rel_total += r_a
        if f_a == 1.0 and r_a == 1.0: a_passed += 1
        
        f_b, r_b = eval_b.get('faithfulness', 0.0), eval_b.get('relevance', 0.0)
        b_faith_total += f_b; b_rel_total += r_b
        if f_b == 1.0 and r_b == 1.0: b_passed += 1
        
        print(f"   🤖 Strategy A Answer: \"{ans_a}\"")
        print(f"      ↳ Scores -> Faith: {f_a} | Rel: {r_a} | Reason: {eval_a.get('reason')}")
        print(f"   🛡️ Strategy B Answer: \"{ans_b}\"")
        print(f"      ↳ Scores -> Faith: {f_b} | Rel: {r_b} | Reason: {eval_b.get('reason')}")
        print("-" * 60 + "\n")
        
        time.sleep(0.5) # Increased padding slightly to avoid rate limits on the new SDK

    elapsed_time = time.time() - start_time

    a_acc = (a_passed / total_tests) * 100; b_acc = (b_passed / total_tests) * 100
    a_f = (a_faith_total / total_tests) * 100; b_f = (b_faith_total / total_tests) * 100
    a_r = (a_rel_total / total_tests) * 100; b_r = (b_rel_total / total_tests) * 100

    print("═"*60)
    print("📊 LIVE PROMPT OPTIMIZATION SCORECARD")
    print("═"*60)
    print(f"⏱️ Evaluation Time: {elapsed_time:.2f} seconds")
    print("-" * 60)
    print("METRIC             | STRATEGY A (LOOSE) | STRATEGY B (STRICT) | DELTA ")
    print("-" * 60)
    print(f"System Accuracy    |      {a_acc:.1f}%          |       {b_acc:.1f}%          |  +{b_acc - a_acc:.1f}% 🔥")
    print(f"Avg Faithfulness   |      {a_f:.1f}%          |       {b_f:.1f}%          |  +{b_f - a_f:.1f}% 🛡️")
    print(f"Avg Relevance      |      {a_r:.1f}%          |       {b_r:.1f}%          |  +{b_r - a_r:.1f}% 🎯")
    print("═"*60 + "\n")