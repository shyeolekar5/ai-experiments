// Projects with a real README worth fetching live rather than paraphrasing.
// `raw` is what the Worker fetches from; `citeUrl` is what gets shown to
// visitors as the clickable source link (the human-readable GitHub page,
// not the raw content URL).

export interface GithubSource {
  label: string;
  raw: string;
  citeUrl: string;
}

export const GITHUB_SOURCES: GithubSource[] = [
  {
    label: "Project — AI Document Pipeline (document-management-system)",
    raw: "https://raw.githubusercontent.com/shyeolekar5/ai-experiments/main/document-management-system/docs/README.md",
    citeUrl: "https://github.com/shyeolekar5/ai-experiments/blob/main/document-management-system/docs/README.md",
  },
  {
    label: "Project — Rental Direct-Booking Site",
    raw: "https://raw.githubusercontent.com/shyeolekar5/ai-experiments/main/rental-direct-booking-site/docs/README.md",
    citeUrl: "https://github.com/shyeolekar5/ai-experiments/blob/main/rental-direct-booking-site/docs/README.md",
  },
  {
    label: "Project — Voice-to-Trello Automation",
    raw: "https://raw.githubusercontent.com/shyeolekar5/ai-experiments/main/voice-to-trello-automation/README.md",
    citeUrl: "https://github.com/shyeolekar5/ai-experiments/tree/main/voice-to-trello-automation",
  },
  {
    label: "Project — Customer Personality Analysis (DeepCollab)",
    raw: "https://raw.githubusercontent.com/shyeolekar5/DeepCollab/main/README.md",
    citeUrl: "https://github.com/shyeolekar5/DeepCollab",
  },
];
