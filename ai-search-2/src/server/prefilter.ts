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

  // Fabricated scoring or an unauthorized hiring verdict — no source has a
  // "match %", and a flat yes/no "good fit for this role" judgment against
  // a pasted job description is just as invented, even without a number
  // attached. Catches "match % / score", "good match/fit for this role",
  // "is she qualified for", "should I hire her", regardless of how long
  // the accompanying job description text is.
  /match\s*%|match(ing)?\s*(percentage|score)|\brate her fit\b|\bscore (her|this)\b/i,
  /\b(match|fit)\b[^.?!]{0,60}\b(this|the)\s*(role|job|position)\b/i,
  /\bis she (a |be a )?(good|strong|great|bad|weak|poor|right)?\s*(match|fit|hire)\b/i,
  /\bshould (i|we|you) hire her\b/i,
  /\bis she qualified for\b/i,
  /\bwould she be (a )?(good|great|strong)?\s*(fit|match|hire)\b/i,

  // Opinions about named third parties
  /(opinion|think) (of|about) (her|his|their) (boss|manager|employer|colleague|coworker|company)/i,
];

export function isBlocked(question: string): boolean {
  return BLOCKED_PATTERNS.some((pattern) => pattern.test(question));
}

export const BLOCKED_RESPONSE =
  `<p>That's not something I can answer here — <a href="${LINKEDIN_URL}" target="_blank" rel="noopener">connect with Shraddha on LinkedIn</a> instead.</p>`;
