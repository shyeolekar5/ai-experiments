Each section below is a separate labeled source. When answering, cite the exact "Source" label and "URL" of every section you draw from.

---

## Source: Resume — Forward Deployed Product Manager
URL: https://github.com/shyeolekar5/ai-experiments

SHRADDHA YEOLEKAR
Forward Deployed Product Manager — AI Deployment & Solutions Strategy
linkedin.com/in/shraddha-yeolekar • github.com/shyeolekar5

SUMMARY
Forward-deployed AI Product Manager who embeds with engineering, compliance, and regional stakeholders to turn live production issues into roadmap decisions, not backlog tickets. Owns the deployment lifecycle for AI systems — architecture debate, vendor evaluation, CI/CD-based release (CircleCI, Kubernetes, ArgoCD) — reading logs and dashboards directly rather than relying on status reports. Not an engineer, but technical enough to work shoulder-to-shoulder with one. Deploying AI foundation from the University of Toronto plus a Master's in Management.

CORE SKILLS
Deployment & Solutioning: CI/CD (CircleCI), Kubernetes, ArgoCD, RAG/LLM Architecture, REST API Integration, Production Monitoring & Release Ownership
Field & Stakeholder Leadership: Cross-Functional Steering Committees, Senior Leadership Communication, Customer/Stakeholder Workshops, Compliance Navigation, Change Management
GenAI Foundation: LLMs (GPT-4, Gemini), RAG, Semantic Search, Vector Embeddings, Prompt Engineering, Sentiment Analysis
Build-vs-Buy & ROI: Vendor Evaluation & Selection, ROI Modeling, Backlog Prioritization, Agile/Scrum
Data Stack: Python (Pandas, NumPy), SQL, Looker Studio, Git, Jira, Confluence

EXPERIENCE
OANDA, Toronto, Canada — 2021 to Present
Global Manager, Digital Client Experience — AI Product Strategy & Digital Automation
Embeds with engineering, compliance, and regional stakeholders to own the deployment lifecycle for OANDA's AI/automation portfolio — architecture debate, vendor build-vs-buy calls, and production release — carrying each initiative from 0-to-1 discovery through launch and iteration.
- Embeds directly inside Compliance, Engineering, and regional Support workflows, turning live production issues — false escalations, hallucination edge cases — directly into roadmap decisions instead of backlog tickets.
- Debated architecture and ROI trade-offs to select and scale two vendor AI systems to production — a Human-in-the-Loop quality control review program (10,000+ cases/month, ~20 FTE/month saved) and an AI chatbot (+25% monthly deflection, ~4 FTE/year) — building a third system herself where no vendor fit existed.
- Built and launched OANDA's first AI-powered roleplay trainer for skill practice, from scratch, where vendor evaluation showed no fit; early pilot data points to roughly 30% faster new-hire ramp time.
- Defines and tracks the KPIs behind every AI launch — deflection rate, CSAT, resolution time — reading dashboards directly rather than relying on status reports to steer priorities.
- Leads cross-functional steering committees across Product, Engineering, and Compliance, holding the line on scope with stakeholders when needed and keeping AI initiatives aligned to regional ROI targets.
- Serves as the primary product voice to senior leadership on the health and trajectory of the AI/automation portfolio, translating technical trade-offs and results into terms that inform investment and prioritization decisions.
- Owns end-to-end regulatory approval for every AI launch — human-in-the-loop review, PII controls, jurisdiction-by-jurisdiction sign-off — securing zero PII or unauthorized-advice incidents to date.

Content Lead — AI Strategy, Chatbot Implementation & Automations (OANDA, earlier role)
Owned AI strategy and automation delivery for the client-experience org — identifying automation use cases and taking them from platform migration through daily operational tooling.
- Led OANDA's migration from predictive AI (Salesforce Einstein) to a Generative AI/RAG architecture, lifting global deflection 15% while holding hallucination rates under 1% since launch — running hands-on evaluations of Agentforce and third-party vendors before recommending the future state.
- Partnered shoulder-to-shoulder with Engineering on release pipelines (CircleCI, Kubernetes, ArgoCD) for RAG-based LLM services — owning release readiness and rollback criteria, and reading logs and monitoring dashboards directly.
- Led cross-functional pilots for agent-facing AI — automated summarization, sentiment analysis, and intelligent recommended responses — iterating directly with front-line teams.
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
