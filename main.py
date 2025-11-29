import os
import json
import random
from datetime import datetime
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# ====== CONFIG ======

# Your affiliate links – start with ySense, add more later
AFFILIATE_LINKS = [
    {
        "name": "ySense",
        "url": "https://www.ysense.com/?rb=225271775",
        "weight": 1.0,  # how often this one gets shown
    },
    # Add more later, e.g.
    # {"name": "FreeCash", "url": "https://your-freecash-link", "weight": 1.0},
]

LEADS_FILE = "leads.json"
CLICKS_FILE = "clicks.json"


# ====== HELPERS ======

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def choose_affiliate() -> dict:
    """Choose an affiliate link using weights."""
    total_weight = sum(a["weight"] for a in AFFILIATE_LINKS)
    r = random.uniform(0, total_weight)
    upto = 0
    for a in AFFILIATE_LINKS:
        if upto + a["weight"] >= r:
            return a
        upto += a["weight"]
    return AFFILIATE_LINKS[0]


# ====== ROUTES ======

LANDING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fast Payouts Every Day</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #050816;
            color: #f9fafb;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .card {{
            background: rgba(15,23,42,0.95);
            border-radius: 18px;
            padding: 24px 20px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 18px 45px rgba(0,0,0,0.6);
        }}
        h1 {{
            font-size: 1.6rem;
            margin-bottom: 4px;
        }}
        h2 {{
            font-size: 0.95rem;
            font-weight: 400;
            color: #a5b4fc;
            margin-top: 0;
            margin-bottom: 18px;
        }}
        label {{
            font-size: 0.8rem;
            display: block;
            margin-bottom: 4px;
            color: #cbd5f5;
        }}
        input, select {{
            width: 100%;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid #1e293b;
            background: #020617;
            color: #f9fafb;
            margin-bottom: 12px;
            font-size: 0.9rem;
        }}
        button {{
            width: 100%;
            padding: 11px 14px;
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg,#22c55e,#16a34a);
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
        }}
        button:active {{
            transform: scale(0.98);
        }}
        .note {{
            font-size: 0.7rem;
            color: #9ca3af;
            margin-top: 6px;
        }}
    </style>
</head>
<body>
  <div class="card">
    <h1>Fast Payouts Every Day</h1>
    <h2>SideHustle Genie · Powered by Miraplexity</h2>

    <form method="post" action="/signup">
      <label for="email">Email to send your earning apps</label>
      <input id="email" name="email" type="email" required placeholder="you@example.com" />

      <label for="country">Country (optional)</label>
      <input id="country" name="country" type="text" placeholder="United States" />

      <label for="goal">Daily cash goal</label>
      <select id="goal" name="goal">
        <option value="$5">$5 / day</option>
        <option value="$10">$10 / day</option>
        <option value="$20" selected>$20 / day</option>
        <option value="$50">$50 / day</option>
      </select>

      <input type="hidden" name="source" value="{{ source }}" />

      <button type="submit">Unlock My Fast-Payout Apps</button>
      <div class="note">
        No spam. You’ll get a list of legit apps that pay for real tasks.
      </div>
    </form>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def landing():
    source = request.args.get("src", "direct")
    return render_template_string(LANDING_HTML, source=source)


@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email", "").strip().lower()
    country = request.form.get("country", "").strip()
    goal = request.form.get("goal", "").strip()
    source = request.form.get("source", "direct")

    if not email:
        return redirect("/")

    leads = load_json(LEADS_FILE, [])
    leads.append(
        {
            "email": email,
            "country": country,
            "goal": goal,
            "source": source,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    )
    save_json(LEADS_FILE, leads)

    # After capture, send them to the rotator
    return redirect("/go")


@app.route("/go", methods=["GET"])
def go():
    src = request.args.get("src", "direct")

    target = choose_affiliate()

    clicks = load_json(CLICKS_FILE, [])
    clicks.append(
        {
            "name": target["name"],
            "url": target["url"],
            "source": src,
            "ts": datetime.utcnow().isoformat() + "Z",
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        }
    )
    save_json(CLICKS_FILE, clicks)

    return redirect(target["url"])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
