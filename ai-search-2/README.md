# Ask Me Anything

A document-grounded Q&A tool answering questions about Shraddha Yeolekar's real background — resume and GitHub projects — instead of a static page. Live at [ask.shraddhayeolekar.com](https://ask.shraddhayeolekar.com).

Successor to the original `ai-search` project (FastAPI + Gemini, PDF-based): same underlying idea, rebuilt on Cloudflare Workers, re-grounded in personal/career content instead of a research paper, and hardened against the real risks of a public-facing LLM persona bot.

## How it works

- **Grounding**: a static file (`grounding/context.md`, resume + undocumented projects) plus four GitHub READMEs fetched live and cached for 24h (`document-management-system`, `rental-direct-booking-site`, `voice-to-trello-automation`, `DeepCollab`) — so those stay current automatically without a manual update loop.
- **Answering**: Gemini, called directly via REST (no SDK), with structured JSON output (`answer` + `citations`) so every claim links back to a real source rather than free-text that might invent one.
- **Guardrails, in order**: a deterministic keyword pre-filter blocks risky question categories (compensation, negative/comparative framing, protected-class topics, jailbreak attempts) *before* Gemini is ever called → Turnstile spam check → a hardened system prompt with explicit refusal categories → citation validation (any citation not matching a real known source gets dropped) → a per-visitor daily rate limit → a KV-backed kill switch that can disable the whole feature instantly without a redeploy.
- **Logging**: every question/answer pair (and whether the pre-filter blocked it) goes to D1, so the actual traffic can be reviewed rather than assumed safe.

## Stack

Cloudflare Workers (compute + static hosting), Cloudflare KV (kill switch, rate limiting, GitHub content cache), Cloudflare D1 (query log), Cloudflare Turnstile (spam protection), Google Gemini (`gemini-2.5-flash`, structured output).

## Local development

```sh
npm install
cp .dev.vars.example .dev.vars   # fill in GEMINI_API_KEY at minimum
npx wrangler d1 execute ai-search-2-db --local --file=./schema.sql
npm run dev
```

## Deployment

Connected to Cloudflare via Workers Builds — push to `main`, it builds and deploys automatically. Required setup (one-time): create the KV namespace and D1 database, apply `schema.sql` to the remote database, set `GEMINI_API_KEY` and `TURNSTILE_SECRET_KEY` as secrets, set `PUBLIC_TURNSTILE_SITE_KEY` in `public/index.html`.

**Kill switch**: `npx wrangler kv key put --binding=KV "search_enabled" "false" --remote` disables search instantly; `"true"` re-enables it.
