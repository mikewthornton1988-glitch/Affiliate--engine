import os
import json
import datetime
from flask import Flask, request, redirect, make_response

app = Flask(__name__)

# ------------- CONFIG -------------

# Your ySense affiliate link
AFFILIATE_URL = "https://www.ysense.com/?rb=225271775"

# File to store click/view logs (simple JSON)
DATA_FILE = "clicks.json"

# ------------- DATA HELPERS -------------

def load_events():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)


def record_event(event_type: str, source: str) -> None:
    events = load_events()
    events.append({
        "type": event_type,
        "source": source,
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent", ""),
        "ts_utc": datetime.datetime.utcnow().isoformat() + "Z",
    })
    save_events(events)


# ------------- HTML TEMPLATES -------------

LANDING_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>3 Fast Payout Apps A Day</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #050816;
      color: #f7f7f7;
      margin: 0;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }}
    .card {{
      max-width: 480px;
      width: 100%;
      padding: 24px 20px 28px;
      background: linear-gradient(135deg, #111827, #020617);
      border-radius: 18px;
      box-shadow: 0 20px 45px rgba(0,0,0,0.4);
      border: 1px solid rgba(148,163,184,0.35);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(34,197,94,0.16);
      color: #bbf7d0;
      border: 1px solid rgba(34,197,94,0.55);
    }}
    h1 {{
      font-size: 22px;
      line-height: 1.25;
      margin: 14px 0 6px;
    }}
    .sub {{
      font-size: 13px;
      color: #cbd5f5;
      margin-bottom: 18px;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0 0 18px;
      font-size: 13px;
      color: #e5e7eb;
    }}
    ul li {{
      margin-bottom: 6px;
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }}
    ul li span.icon {{
      font-size: 16px;
      margin-top: 1px;
    }}
    .btn {{
      display: block;
      width: 100%;
      text-align: center;
      padding: 11px 16px;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #22c55e, #16a34a);
      color: #022c22;
      border-radius: 999px;
      font-weight: 600;
      font-size: 15px;
      text-decoration: none;
      border: none;
    }}
    .btn:hover {{
      filter: brightness(1.05);
    }}
    .note {{
      font-size: 11px;
      color: #9ca3af;
      margin-bottom: 6px;
    }}
    .disclaimer {{
      font-size: 10px;
      color: #6b7280;
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <main class="card">
    <div class="badge">
      ⚡ Same-day starter
    </div>

    <h1>Turn slow days into <strong>paid days</strong></h1>
    <p class="sub">
      I test money apps so you do not have to. Start with the one I actually use to get small, fast payouts.
    </p>

    <ul>
      <li><span class="icon">✅</span><span>Legit GPT site I am personally using (not a random list of 50 apps).</span></li>
      <li><span class="icon">⏱️</span><span>Setup in about 5 minutes, then check in whenever you have dead time.</span></li>
      <li><span class="icon">🎯</span><span>Best for broke-but-serious people who want $5–$20/week to start.</span></li>
    </ul>

    <a class="btn" href="/go?src=landing_main">
      Tap here to start with my #1 app
    </a>

    <p class="note">
      Your visit source: <strong>{source_label}</strong>
    </p>

    <p class="disclaimer">
      Results vary. This is not a job. It works best if you actually log in daily and clear offers/surveys.
      I may earn a referral commission if you sign up and use the site.
    </p>
  </main>
</body>
</html>
"""

STATS_HTML_HEADER = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Affiliate Engine Stats</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #020617;
      color: #e5e7eb;
      margin: 0;
      padding: 16px;
    }}
    h1 {{
      font-size: 20px;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid #1f2937;
      padding: 6px 4px;
      text-align: left;
    }}
    th {{
      background: #020617;
      font-weight: 600;
    }}
    .tag {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 999px;
      background: rgba(59,130,246,0.18);
      color: #bfdbfe;
    }}
  </style>
</head>
<body>
<h1>Affiliate Engine – Traffic Stats</h1>
<p style="font-size:12px;color:#9ca3af;">
  Simple counts by source (views and clicks). Use <code>?key=secret123</code> to hide this page from random people.
</p>
"""

STATS_HTML_FOOTER = """
</body>
</html>
"""

# ------------- ROUTES -------------

@app.route("/")
def landing():
    """
    Landing page: ?src=fb, ?src=tg, ?src=reels, etc.
    Records a 'view' event and sets a cookie so we keep the same source on /go.
    """
    source = request.args.get("src", "direct")
    record_event("view", source)

    # store source for later redirect
    resp = make_response(LANDING_HTML.format(source_label=source))
    resp.set_cookie("src", source, max_age=60 * 60 * 24 * 30)  # 30 days
    return resp


@app.route("/go")
def go():
    """
    Redirect to ySense using your affiliate link.
    Keeps/records the traffic source.
    """
    source = request.args.get("src") or request.cookies.get("src") or "direct"
    record_event("click", source)

    sep = "&" if "?" in AFFILIATE_URL else "?"
    target = f"{AFFILIATE_URL}{sep}src={source}"
    return redirect(target, code=302)


@app.route("/stats")
def stats():
    """
    Very simple stats dashboard.
    Optional access key: /stats?key=secret123
    """
    access_key = request.args.get("key", "")
    if access_key != os.getenv("STATS_KEY", "secret123"):
        return "Unauthorized. Add ?key=secret123 (or set STATS_KEY env).", 401

    events = load_events()
    by_source = {}

    for e in events:
        src = e.get("source", "unknown")
        if src not in by_source:
            by_source[src] = {"views": 0, "clicks": 0}
        if e.get("type") == "view":
            by_source[src]["views"] += 1
        elif e.get("type") == "click":
            by_source[src]["clicks"] += 1

    rows = []
    for src, data in sorted(by_source.items(), key=lambda x: x[0]):
        v = data["views"]
        c = data["clicks"]
        ctr = (c / v * 100.0) if v else 0.0
        rows.append(
            f"<tr><td><span class='tag'>{src}</span></td>"
            f"<td>{v}</td><td>{c}</td><td>{ctr:.1f}%</td></tr>"
        )

    html = [STATS_HTML_HEADER]
    html.append("<table><thead><tr><th>Source</th><th>Views</th><th>Clicks</th><th>CTR</th></tr></thead><tbody>")
    html.extend(rows)
    html.append("</tbody></table>")
    html.append(STATS_HTML_FOOTER)
    return "".join(html)


# ------------- ENTRYPOINT -------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
