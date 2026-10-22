Each section below is a separate labeled source. When answering, cite the exact "Source" label and "URL" of every section you draw from.

---

## Source: Resume
URL: https://github.com/shyeolekar5/ai-experiments

SHRADDHA YEOLEKAR
AI agent deployment · Customer experience · Regulated industries
linkedin.com/in/shraddha-yeolekar • github.com/shyeolekar5

SUMMARY
Takes AI from vendor evaluation to production in customer experience, in a regulated industry where a wrong answer has consequences. At OANDA, owns the AI and automation portfolio for client experience: build-vs-buy decisions, launch and rollback criteria, regulatory sign-off, and the KPIs behind every launch, with zero PII or unauthorized-advice incidents to date. Not an engineer, but technical enough to read the logs, design the evaluation, and build a working system when no vendor fits. Certificate in Deploying AI from the University of Toronto and a Master's in Management.

CORE SKILLS
AI Deployment & Evaluation: RAG/LLM Architecture, Evaluation Design (golden datasets, LLM-as-a-judge), Guardrails, Release Readiness & Rollback Criteria, Production Monitoring
Regulated Launches: Compliance Sign-off, Human-in-the-Loop Review, PII Controls, Change Management
Build-vs-Buy & ROI: Vendor Evaluation & Selection, ROI Modeling, Backlog Prioritization, Agile/Scrum
Stakeholder Leadership: Cross-Functional Steering Committees, Senior Leadership Communication, Customer/Stakeholder Workshops
GenAI & Data: LLMs (GPT-4, Gemini), Semantic Search, Vector Embeddings, Prompt Engineering, Sentiment Analysis, Python (Pandas, NumPy), SQL, Looker Studio
Delivery Tools: CI/CD (CircleCI), Kubernetes, ArgoCD, REST API Integration, Git, Jira, Confluence

EXPERIENCE
OANDA, Toronto, Canada — 2021 to Present
Global Manager, Digital Client Experience
Owns OANDA's AI and automation portfolio for client experience: build-vs-buy decisions, launch criteria, regulatory sign-off, and the KPIs behind every launch.
- Owns end-to-end regulatory approval for every AI launch (human-in-the-loop review, PII controls, jurisdiction-by-jurisdiction sign-off), with zero PII or unauthorized-advice incidents to date.
- Weighed architecture and ROI trade-offs to select two vendor AI systems and take them to production: an AI chatbot (+25% monthly deflection, ~4 FTE/year) and a human-in-the-loop quality review program (10,000+ cases/month, ~20 FTE/month saved). Built a third system herself where no vendor fit.
- Built and launched OANDA's first AI-powered roleplay trainer for skill practice after vendor evaluation showed no fit; early pilot data points to roughly 30% faster new-hire ramp time.
- Defines and tracks the KPIs behind every AI launch (deflection rate, CSAT, resolution time), reading dashboards directly to steer priorities.
- Turns live production issues, such as false escalations and hallucination edge cases, into roadmap decisions, working directly with Compliance, Engineering, and regional Support.
- Leads steering committees across Product, Engineering, and Compliance, holding the line on scope and keeping AI initiatives aligned to regional ROI targets.
- Reports to senior leadership on the health and direction of the AI and automation portfolio, translating technical trade-offs into investment and prioritization decisions.

Content Lead (OANDA, earlier role)
Owned AI strategy and automation delivery for the client-experience org, from identifying use cases through platform migration and daily operational tooling.
- Led OANDA's migration from predictive AI (Salesforce Einstein) to a Generative AI/RAG architecture, lifting global deflection 15% while holding hallucination rates under 1% since launch, after hands-on evaluations of Agentforce and third-party vendors.
- Owned release readiness and rollback criteria for RAG-based LLM services, working with Engineering on release pipelines (CircleCI, Kubernetes, ArgoCD) and reading logs and monitoring dashboards directly.
- Led cross-functional pilots for agent-facing AI (automated summarization, sentiment analysis, and recommended responses), iterating directly with front-line teams.
- Automated manual reporting into live dashboards, replacing periodic updates with daily visibility and saving an estimated 30 hours/month of manual work.

EARLY CAREER
Co-founder, Brand Communication & Strategy — Spider Content Inc., Canada & Asia, 2014-2021. Built and led a team of 7+ across strategy, content, and delivery for clients across Canada and Asia.
Category Manager, Hair Care — Raymond Limited, Mumbai, India, 2012-2014. Owned P&L, product portfolio, and market/distribution strategy for the category at national retail scale.

EDUCATION & CERTIFICATIONS
Certificate in Deploying AI (2026) — University of Toronto, Canada
Certificate in Data Science and Machine Learning (2025) — University of Toronto, Canada
Master's in Management (Marketing) — IES Management College, Mumbai, India
Languages: English (Fluent), French (Intermediate)

---

## Source: Project — RAG Evaluation Framework (ai-evals)
URL: https://github.com/shyeolekar5/ai-experiments/tree/main/ai-evals

Five versioned audit pipelines comparing chunking and retrieval strategies for a RAG system: no-chunking with a gatekeeper check, no-chunking with a synthesizer, chunk-by-heading, chunk-with-hierarchy, and no-chunking with long-context. Built to systematically compare retrieval-quality trade-offs rather than picking a chunking strategy by instinct.
Stack: Python, Google Gemini.

---

## Source: Project — Guardrail & Judge Evaluation (ai-evals-2)
URL: https://github.com/shyeolekar5/ai-experiments/tree/main/ai-evals-2

Compares a "loose" prompt strategy (explicitly told to bend rules to keep customers happy — designed to surface hallucination and guardrail-violation risk) against a guardrailed, strictly-anchored prompt strategy, using DeepEval's LLM-as-a-judge metrics (Faithfulness, Answer Relevancy) to score both quantitatively rather than by eyeballing outputs.
Stack: Python, Google Gemini, DeepEval.

---

## Source: Project — Multi-Agent Support Orchestrator (ai-orchestration)
URL: https://github.com/shyeolekar5/ai-experiments/tree/main/ai-orchestration

A from-scratch multi-agent routing demo: a Router Agent classifies each incoming message as a knowledge-base question or an angry/escalation case. Knowledge-base questions go to a hand-built in-memory vector store (cosine similarity computed in pure Python, no vector database) for semantic search, then a KB Support Agent drafts an answer grounded only in the retrieved chunk. Escalation cases go to a separate Escalation Agent that drafts a human hand-off ticket summary with an urgency label. Every LLM and embedding call is wrapped with observability logging showing latency and token counts in real time.
Stack: Python, Google Gemini (generation + embeddings).

---

## Source: Project — AI Site Search
URL: https://github.com/shyeolekar5/ai-experiments/tree/main/ai-search-2

A document-grounded Q&A service — originally a FastAPI backend serving semantic search over a PDF via Gemini, since rebuilt on Cloudflare Workers (the same architecture as this very tool you're using right now to ask questions). Answers only from a defined set of source material, cites which source it drew from, and refuses to speculate or answer outside its grounding.
Stack: TypeScript, Cloudflare Workers, Cloudflare KV, Cloudflare D1, Google Gemini, Cloudflare Turnstile.

---

Note: document-management-system, rental-direct-booking-site, voice-to-trello-automation, and DeepCollab are documented via their own READMEs, fetched live and cached separately — not duplicated in this file. When describing DeepCollab specifically, remember it was a 5-person team project; Shraddha's role was preprocessing, pipeline automation, and K-means clustering — never imply she built it solo.
