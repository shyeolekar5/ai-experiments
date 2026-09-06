/// <reference types="@cloudflare/workers-types" />
// Handles POST /api/enquire, called from src/worker.ts.
// Validates input, checks Turnstile (if configured), and emails the owner via Resend.
//
// Required secrets (set via `wrangler secret put <NAME>`, or in the Cloudflare dashboard under
// the Worker's Settings → Variables and Secrets):
//   RESEND_API_KEY     — from resend.com
//   NOTIFY_EMAIL       — where enquiries should be sent (the owner's inbox)
//   FROM_EMAIL         — a verified sender, e.g. enquiries@yourdomain.com
// Optional:
//   TURNSTILE_SECRET_KEY — enables spam-check verification when set

export interface Env {
  ASSETS: Fetcher;
  RESEND_API_KEY: string;
  NOTIFY_EMAIL: string;
  FROM_EMAIL: string;
  TURNSTILE_SECRET_KEY?: string;
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));
}

export async function handleEnquire(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") {
    return Response.json({ error: "Method not allowed." }, { status: 405 });
  }

  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }

  const name = String(body.name || "").trim();
  const email = String(body.email || "").trim();
  const checkIn = String(body.checkIn || "").trim();
  const checkOut = String(body.checkOut || "").trim();
  const guests = String(body.guests || "").trim();
  const stay = String(body.stay || "short").trim();
  const message = String(body.message || "").trim();
  const turnstileToken = String(body["cf-turnstile-response"] || "").trim();

  if (!name || !email) {
    return Response.json({ error: "Name and email are required." }, { status: 400 });
  }
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) {
    return Response.json({ error: "Please enter a valid email address." }, { status: 400 });
  }

  if (env.TURNSTILE_SECRET_KEY) {
    if (!turnstileToken) {
      return Response.json({ error: "Spam check failed — please retry." }, { status: 400 });
    }
    const verifyRes = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        secret: env.TURNSTILE_SECRET_KEY,
        response: turnstileToken,
        remoteip: request.headers.get("CF-Connecting-IP") || undefined,
      }),
    });
    const verify = await verifyRes.json<{ success: boolean }>();
    if (!verify.success) {
      return Response.json({ error: "Spam check failed — please retry." }, { status: 400 });
    }
  }

  const subject = `Enquiry: ${name} · ${checkIn || "no dates"}${checkOut ? " – " + checkOut : ""} · ${guests || "?"} guests`;
  const html = `
    <h2>New direct-booking enquiry</h2>
    <p><strong>Name:</strong> ${escapeHtml(name)}</p>
    <p><strong>Email:</strong> ${escapeHtml(email)}</p>
    <p><strong>Check-in:</strong> ${escapeHtml(checkIn) || "—"}</p>
    <p><strong>Check-out:</strong> ${escapeHtml(checkOut) || "—"}</p>
    <p><strong>Guests:</strong> ${escapeHtml(guests) || "—"}</p>
    <p><strong>Type of stay:</strong> ${escapeHtml(stay)}</p>
    <p><strong>Message:</strong><br>${escapeHtml(message).replace(/\n/g, "<br>") || "—"}</p>
  `;

  if (!env.RESEND_API_KEY || !env.NOTIFY_EMAIL || !env.FROM_EMAIL) {
    // Not configured yet — fail loudly rather than silently dropping enquiries.
    console.error("Enquiry received but email is not configured:", { name, email, checkIn, checkOut, guests, stay, message });
    return Response.json({ error: "Enquiries aren't wired up to email yet — please contact us directly for now." }, { status: 503 });
  }

  const emailRes = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({
      from: env.FROM_EMAIL,
      to: env.NOTIFY_EMAIL.split(",").map((e) => e.trim()).filter(Boolean),
      reply_to: email,
      subject,
      html,
    }),
  });

  if (!emailRes.ok) {
    const errText = await emailRes.text();
    console.error("Resend error:", errText);
    return Response.json({ error: "Could not send your enquiry right now. Please try again shortly." }, { status: 502 });
  }

  return Response.json({ ok: true });
}
