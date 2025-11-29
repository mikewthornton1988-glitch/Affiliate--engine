from flask import Flask, render_template_string

app = Flask(__name__)

# ==============================
# YOUR AFFILIATE LINK
# ==============================
AFFILIATE_LINK = "https://www.ysense.com/?rb=225271775"

# ==============================
# LANDING PAGE TEMPLATE
# ==============================
LANDING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Fast Payout Earnings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
        body {
            background: #0d0d0d;
            color: white;
            font-family: Arial, Helvetica, sans-serif;
            padding: 20px;
            text-align: center;
        }
        .box {
            background: #111;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #333;
            max-width: 500px;
            margin: auto;
        }
        button {
            background: #ffcc00;
            border: none;
            padding: 15px;
            width: 80%;
            margin-top: 20px;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .footer {
            margin-top: 35px;
            font-size: 0.85em;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>Earn Fast — 3 Payouts Every Day</h1>
        <p>Start earning instantly with real tasks, fast payouts, and daily bonuses.</p>

        <button onclick="window.location.href='{{ affiliate }}'">
            Start Now (Free)
        </button>
    </div>

    <div class="footer">
        Powered by Mike's Affiliate Engine
    </div>
</body>
</html>
"""

# ==============================
# ROUTES
# ==============================
@app.route("/", methods=["GET"])
def home():
    return render_template_string(LANDING_HTML, affiliate=AFFILIATE_LINK)

# ==============================
# START SERVER FOR RENDER
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
