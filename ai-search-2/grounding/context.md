Each section below is a separate labeled source. When answering, cite the exact "Source" label and "URL" of every section you draw from.

---

## Source: Resume
URL: https://github.com/shyeolekar5/ai-experiments

SHRADDHA YEOLEKAR
AI agent deployment · Customer experience · Regulated industries
shraddhayeolekar.com • linkedin.com/in/shraddha-yeolekar • github.com/shyeolekar5

SUMMARY
Has spent five years taking AI agents and automation from discovery to production at OANDA, a regulated online trading company. Evaluates vendors, defines success criteria, designs the evaluations and guardrails, gets compliance sign-off, and works with support teams until the AI is adopted and measurably better. Also builds and deploys AI tools herself in Python and TypeScript by directing AI coding tools such as Claude Code, then reviewing and testing what they produce. Before OANDA, co-founded and ran a content agency for seven years, pitching, scoping and delivering work for clients in four countries. Her strength is deciding when an AI agent is ready to launch and backing that decision with evidence.

KEY RESULTS
- +25% monthly case deflection from an AI chatbot
- Hallucination rate under 1% since launch
- Zero PII or unauthorized-advice incidents to date

CORE SKILLS
AI agent deployment, conversational AI, conversation design, human hand-off, transcript review, customer support automation, vendor evaluation, success criteria and KPIs, evaluation frameworks, guardrails, human-in-the-loop review, compliance and risk, stakeholder management, client management, training and enablement, change management

EXPERIENCE
OANDA, Toronto, Canada — 2021 to Present

Global Manager, Digital Client Experience
Owns OANDA's AI and automation portfolio for client experience, from discovery and vendor selection through launch, compliance approval and ongoing improvement.
- AI agent deployment: Led the move from OANDA's earlier predictive chatbot to a generative AI and RAG chatbot, after hands-on evaluations of several vendors. It raised monthly case deflection by 25% and has kept hallucination under 1% since launch. It serves clients in several markets, in English and French.
- Vendor evaluation and build-vs-buy: Compares vendor AI systems on architecture, cost and ROI before committing. Where no vendor fit, as with the roleplay trainer, she built the solution herself.
- AI for agent training: Built OANDA's first AI roleplay trainer with AI coding tools and deployed it to production, so new support hires can practise their skills.
- Training and enablement: Trains support teams on each new AI tool and writes the guides they use to work with it.
- Quality assurance: Scaled a human-in-the-loop quality review program that uses AI to reduce manual review work.
- Compliance and risk: Owns regulatory approval for every AI launch, including human review, PII controls and sign-off in each jurisdiction. There have been no PII or unauthorized-advice incidents to date.
- Success criteria and KPIs: Defines the metrics for every AI launch (deflection rate, CSAT and resolution time) and tracks them in live dashboards to decide what to improve next.
- Release readiness: Sets the release and rollback criteria for LLM services and works with Engineering on the release pipeline, reading logs and monitoring dashboards directly after each launch.
- Production issues and product feedback: Works inside Compliance, Engineering and regional Support teams to turn live problems, such as false escalations and hallucination edge cases, into roadmap decisions.
- Stakeholder management: Leads steering committees with Product, Engineering and Compliance, holds the line on scope, and keeps each AI initiative tied to ROI targets.
- Executive communication: Briefs senior leadership on the health of the AI portfolio, explaining technical trade-offs in plain terms so they can make investment and priority decisions.

Content Lead (OANDA, earlier role)
Owned AI strategy and automation delivery for the client experience team, from finding use cases to running them day to day.
- Conversation design: Designed more than 30 conversation flows for a predictive chatbot, including the hand-off from the bot to human agents.
- CRM integration: Led the chatbot's integration with the support team's CRM, with live routing to available agents and automatic case creation when no agent was available.
- Transcript review and knowledge base gaps: Used AI to review chatbot transcripts and turn them into clear action items. For example, recurring customer questions led to many new troubleshooting guides being added to the knowledge base.
- Agent-assist pilots: Ran pilots of AI tools for support agents, including automatic summaries, sentiment analysis and suggested responses, and refined them with feedback from front-line teams.
- Automation discovery: Identified automation opportunities across client experience and replaced manual reporting with live dashboards.

SKILLS
AI and LLMs: AI agents, conversational AI, large language models (GPT-4, Gemini), retrieval-augmented generation (RAG), prompt engineering, semantic search, vector embeddings, sentiment analysis, conversation design, knowledge base management
Evaluation and quality: evaluation frameworks, golden datasets, LLM-as-a-judge, DeepEval, guardrails, transcript review, human-in-the-loop review, release and rollback criteria, production monitoring
Technical: AI-assisted development (Claude Code), Python (Pandas, NumPy), TypeScript, SQL, Google Cloud (GCP), Cloudflare Workers, Salesforce Service Cloud (Omni-Channel routing), REST API integrations, CI/CD (CircleCI, Kubernetes, ArgoCD), Git, Looker Studio
Customer and business: client pitches and proposals, project scoping, discovery and requirements, stakeholder workshops, vendor evaluation, ROI modeling, KPI design, change management, executive communication, Agile/Scrum, Jira, Confluence

EARLIER CAREER
Co-founder, Brand Communication & Strategy — Spider Content Inc., Canada, India & Malaysia, 2014-2021.
- Client acquisition: Pitched new clients and built referral partnerships, winning work from clients in India, Malaysia, Canada and the US.
- Scoping and delivery: Wrote proposals, scoped each project and led delivery through to completion.
- Team leadership: Built and led a team of 7+ across strategy, content and delivery, and managed the agency's resourcing across projects.
Category Manager, Hair Care — Raymond Limited, Mumbai, India, 2012-2014. Owned the P&L, product portfolio, and market and distribution strategy for the category at national retail scale.

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
