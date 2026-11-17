// Vercel serverless function: receives the website enquiry form and emails it
// to Everstar through Resend (https://resend.com).
//
// Environment variables (set in Vercel → Project → Settings → Environment Variables):
//   RESEND_API_KEY  required  API key from resend.com
//   ENQUIRY_TO      optional  where enquiries go (default mail@everstar.com.sg)
//   ENQUIRY_FROM    optional  sender, e.g. "Everstar Website <website@everstar.com.sg>"
//                             (default uses Resend's test sender, which can only
//                             deliver to the email address of the Resend account)

const MAX = { name: 120, company: 160, email: 200, service: 80, message: 5000 };
const SERVICES = new Set([
  "Insulation",
  "Surface treatment & coating",
  "Access & scaffolding",
  "Passive fire protection",
  "CUI / insulation design",
  "Several of these",
]);

function clean(value, max) {
  return String(value ?? "").replace(/\r\n?/g, "\n").trim().slice(0, max);
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "Use POST." });
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  // Honeypot: real visitors never see or fill the "website" field.
  if (clean(body.website, 200)) return res.status(200).json({ ok: true });

  const data = {
    name: clean(body.name, MAX.name),
    company: clean(body.company, MAX.company),
    email: clean(body.email, MAX.email),
    service: clean(body.service, MAX.service),
    message: clean(body.message, MAX.message),
  };

  if (!data.name) return res.status(400).json({ ok: false, error: "Enter your name." });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    return res.status(400).json({ ok: false, error: "Enter a valid work email, like name@company.com." });
  }
  if (!SERVICES.has(data.service)) data.service = "Not specified";

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    console.error("enquiry: RESEND_API_KEY is not set");
    return res.status(503).json({ ok: false, error: "not_configured" });
  }

  const to = process.env.ENQUIRY_TO || "mail@everstar.com.sg";
  const from = process.env.ENQUIRY_FROM || "Everstar Website <onboarding@resend.dev>";
  const subject = `Website enquiry: ${data.service} – ${data.company || data.name}`.slice(0, 200);

  const rows = [
    ["Name", data.name],
    ["Company", data.company || "—"],
    ["Email", data.email],
    ["Service", data.service],
  ];
  const text =
    rows.map(([k, v]) => `${k}: ${v}`).join("\n") +
    `\n\nProject details:\n${data.message || "—"}\n\n— Sent from the enquiry form on the Everstar website`;
  const html =
    `<table cellpadding="6" style="font-family:Arial,sans-serif;font-size:14px;border-collapse:collapse">` +
    rows.map(([k, v]) => `<tr><td style="color:#555"><b>${k}</b></td><td>${escapeHtml(v)}</td></tr>`).join("") +
    `</table><p style="font-family:Arial,sans-serif;font-size:14px"><b>Project details</b><br>` +
    `${escapeHtml(data.message || "—").replace(/\n/g, "<br>")}</p>` +
    `<p style="font-family:Arial,sans-serif;font-size:12px;color:#777">Sent from the enquiry form on the Everstar website. Reply to this email to answer ${escapeHtml(data.name)} directly.</p>`;

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from, to: to.split(",").map((s) => s.trim()), reply_to: data.email, subject, text, html }),
    });
    if (!r.ok) {
      console.error("enquiry: Resend error", r.status, await r.text());
      return res.status(502).json({ ok: false, error: "send_failed" });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("enquiry: request failed", err);
    return res.status(502).json({ ok: false, error: "send_failed" });
  }
};
