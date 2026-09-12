Each section below is a separate labeled source. When answering, cite the exact "Source" label and "URL" of every section you draw from.

---

## Source: Resume — Technical AI Product Manager
URL: https://github.com/shyeolekar5/ai-experiments

SHRADDHA YEOLEKAR
Technical AI Product Manager — LLM Systems, Evaluation & Deployment
Toronto, ON • shraddha.goyani@gmail.com • linkedin.com/in/shraddhayeolekar • github.com/shyeolekar5

SUMMARY
Technical AI Product Manager with a track record across product, content, and customer-experience leadership — the recent years spent taking LLM/RAG systems from 0 to 1: setting product vision, debating architecture, and building the evaluation frameworks and guardrails that keep them reliable in production. Comfortable owning ambiguity in a fast-moving environment. Deploying AI foundation from the University of Toronto plus a Master's in Management. Applies the same rigor and data-driven decision-making in her own open-source AI experiments.

CORE SKILLS
LLM Evaluation & Quality: LLM Evaluation Frameworks (DeepEval), Offline/Online Evaluation, Regression Testing, AI Quality Metrics, LLM-as-a-Judge, Hallucination Mitigation, HITL Design
AI & GenAI Architecture: LLMs (GPT-4, Gemini), RAG, Agentic AI Agents, Semantic Search, Vector Embeddings, Prompt Engineering
Deployment & Platform: CI/CD (CircleCI, GitHub Actions), Kubernetes, ArgoCD, REST APIs, Python Automation, Scalable Production Monitoring
Product Leadership & Governance: 0-to-1 Product Launches, Product Vision & Multi-Year Roadmap, Build-vs-Buy & Trade-offs, KPI Definition, Tracking & Prioritization, Cross-Functional Leadership, People Management, Change Management & Adoption, Stakeholder Management, AI Governance & Guardrails

EXPERIENCE
OANDA, Toronto, Canada — 2021 to Present
Global Manager, Digital Client Experience — AI Product Strategy & Digital Automation
Owns the product vision and multi-year roadmap for OANDA's AI/automation portfolio — chatbots, autonomous agents, predictive analytics — carrying each initiative through the full lifecycle, from 0-to-1 discovery through launch and iteration, partnering closely with Data Science, Engineering, Design, Compliance, and Customer Success on every release.
- Delivered OANDA's first client-facing AI system — a chatbot that scaled to +25% monthly case deflection, driving efficiency gains worth roughly 4 FTE/year in manual case handling.
- Delivered OANDA's first internal AI system — a Human-in-the-Loop quality control review program covering 10,000+ cases/month, saving roughly 20 FTE/month and validated against CSAT.
- Built and launched OANDA's first AI-powered roleplay trainer for skill practice, from scratch; early pilot data points to roughly 30% faster new-hire ramp time.
- Defines and tracks the success metrics (KPIs) behind every AI launch — deflection rate, CSAT, resolution time — using them to drive continuous, data-driven iteration.
- Mines support-ticket and usage-pattern data to surface recurring friction points in client and agent workflows, translating findings into prioritized roadmap decisions and product requirements alongside Product, Engineering, and Compliance.
- Runs cross-functional launches with Design and Customer Success on every release, building tight post-launch feedback loops.
- Serves as the primary product voice to senior leadership on the health and trajectory of the AI/automation portfolio.
- Champions a culture of experimentation — running structured experiments on prompt variants, retrieval configurations, and review-flagging thresholds with Data Science before full rollout.
- Designed the guardrails behind every AI launch — human-in-the-loop review, PII controls, jurisdiction-by-jurisdiction sign-off — securing regulatory approval with zero PII or unauthorized-advice incidents to date.

Content Lead — AI Strategy, Chatbot Implementation & Automations (OANDA, earlier role)
Owned AI strategy and automation delivery for the client-experience org.
- Led OANDA's migration from predictive AI to a Generative AI/RAG architecture, lifting global deflection 15% while holding hallucination rates under 1% since launch.
- Automated manual reporting into live dashboards, saving an estimated 30 hours/month of manual work.
- Replaced a translation agency with an automated AI translate-review-publish workflow, cutting translation costs by roughly 80% and turnaround time from days to hours.
- Wrote automation scripts to update titles and descriptions across 600+ site pages.

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
