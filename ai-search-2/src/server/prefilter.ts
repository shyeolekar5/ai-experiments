// Catches risky question categories with a plain keyword/pattern check,
// before the question ever reaches Gemini. Deterministic on purpose — a
// rule can't be argued out of its answer the way a model sometimes can.

import { LINKEDIN_URL } from "./constants";

const BLOCKED_PATTERNS: RegExp[] = [
  // Jailbreak / instruction-override attempts
  /ignore (all|previous|prior|the above)?\s*instructions?/i,
  /pretend (you're|you are|to be)/i,
  /act as (if|a|an)/i,
  /you are now/i,
  /system prompt/i,
  /roleplay/i,
  /jailbreak/i,

  // Negative / comparative framings not okay to have the AI improvise
  /\b(weakness|worst|flaw|fail(ed|ure)?)\b/i,
  /why (shouldn'?t|should not|wouldn'?t)/i,
  /\bfired\b/i,
  /\bregret/i,

  // Compensation / negotiation
  /\bsalary\b/i,
  /compensation/i,
  /\brate\b.*\b(hour|day|charge)/i,

  // Personal / protected-class topics
  /\bage\b|\bhow old\b/i,
  /marital|married|single|dating|relationship status/i,
  /\bpregnan/i,
  /\breligio/i,
  /\bpolitic/i,
  /immigration|visa status|citizenship/i,
  /\bhealth\b|\bdisab(led|ility)/i,

  // Fabricated scoring — no source has a "match %"; any number here would
  // be invented on the spot, not a real fact.
  /match\s*%|match(ing)?\s*(percentage|score)|how good (a |of a )?fit|\brate her fit\b|\bscore (her|this)\b/i,

  // Opinions about named third parties
  /(opinion|think) (of|about) (her|his|their) (boss|manager|employer|colleague|coworker|company)/i,
];

export function isBlocked(question: string): boolean {
  return BLOCKED_PATTERNS.some((pattern) => pattern.test(question));
}

export const BLOCKED_RESPONSE =
  `<p>That's not something I can answer here — <a href="${LINKEDIN_URL}" target="_blank" rel="noopener">connect with Shraddha on LinkedIn</a> instead.</p>`;
