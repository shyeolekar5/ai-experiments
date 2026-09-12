// Catches risky question categories with a plain keyword/pattern check,
// before the question ever reaches Gemini. Deterministic on purpose — a
// rule can't be argued out of its answer the way a model sometimes can.

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

  // Opinions about named third parties
  /(opinion|think) (of|about) (her|his|their) (boss|manager|employer|colleague|coworker|company)/i,
];

export function isBlocked(question: string): boolean {
  return BLOCKED_PATTERNS.some((pattern) => pattern.test(question));
}

export const BLOCKED_RESPONSE =
  "That's not something I can answer here — for anything like that, reach out to Shraddha directly at shraddha.goyani@gmail.com.";
