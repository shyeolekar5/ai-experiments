// Site content that changes over time lives here. To add a project:
//   1. write src/projects/<slug>.html (copy an existing one as a template)
//   2. add an entry to `projects` below, in the order it should be listed
//   3. set `featured: true` on at most three projects for the home page
// Then run `npm run build`.

// The role line shown under the hero and in the footer. One place to change it.
export const ROLE = "AI agent deployment · Customer experience · Regulated industries";

export const projects = [
  {
    slug: "document-pipeline",
    title: "AI Document Pipeline",
    kicker: "Document AI",
    tags: ["Evaluation", "RAG"],
    decision: "Don't ship it yet.",
    why: "The tuned pipeline scored 82% against an 85% bar, with contracts at 60%. The eval gate held it back.",
    featured: true,
  },
  {
    slug: "ask-ai",
    title: "Ask AI",
    kicker: "Live public AI",
    tags: ["Guardrails", "Live"],
    decision: "Run the cheapest, most predictable guardrail before the model.",
    why: "Risky questions are refused by a keyword filter before Gemini is called, and before they count against a visitor's daily limit.",
    featured: true,
  },
  {
    slug: "support-orchestrator",
    title: "Multi-Agent Support Orchestrator",
    kicker: "Agentic AI",
    tags: ["Agentic", "Human-in-the-loop"],
    decision: "Upset customers and exception requests go to a person, not the bot.",
    why: "That's where a fluent wrong answer does the most damage, so the bot writes a hand-off summary instead of a reply.",
    featured: true,
  },
  {
    slug: "guardrail-judge-eval",
    title: "Guardrail & Judge Evaluation",
    kicker: "Evaluation",
    tags: ["Evaluation", "Guardrails"],
    decision: "Test the cases that break support bots, not just the happy path.",
    why: "Eight of twelve test cases are adversarial, and an LLM judge scores both prompts on faithfulness and relevance.",
  },
  {
    slug: "rag-eval-framework",
    title: "RAG Evaluation Framework",
    kicker: "Retrieval",
    tags: ["Evaluation", "RAG"],
    decision: "Change only the retrieval, and hold everything else fixed.",
    why: "Every version uses the same model and prompt, so differences in the answers come from what the model was given.",
  },
  {
    slug: "rental-booking-site",
    title: "Rental Direct-Booking Site",
    kicker: "Client work, shipped",
    tags: ["Client work"],
    decision: "Hold back search indexing until the real domain is live.",
    why: "Indexing the placeholder subdomain would have created a duplicate of the future production site.",
  },
];

// Smaller work: listed on the projects page with an external link, no page of its own.
export const alsoBuilt = [
  {
    title: "Voice-to-Trello",
    text: "Speak a task and get a Trello card: transcription, then AI extraction of title, due date, category and priority.",
    url: "https://github.com/shyeolekar5/ai-experiments/tree/main/voice-to-trello-automation",
  },
  {
    title: "Customer personality analysis",
    text: "A five-person team project on clustering for marketing segmentation. My part was preprocessing, pipeline automation and K-means.",
    url: "https://github.com/shyeolekar5/DeepCollab",
  },
];
