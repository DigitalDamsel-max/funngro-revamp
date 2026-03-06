"""
Funngro Website — Flask Backend
Routes: /, /company, /teens, /contact (POST), 404, 500
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "funngro-dev-secret-2026")

# ── Simple in-memory store (replace with DB in production) ──────────────────
contact_submissions = []


# ── Helpers ─────────────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home — redirect to company page as the main landing."""
    return redirect(url_for("company"))


@app.route("/company")
def company():
    stats = {
        "teens": 12000,
        "projects": 3500,
        "companies": 800
    }

    return render_template("company.html", stats=stats)


@app.route("/teens")
def teens():
    """Teens page — for 13–19 year olds who want to earn."""
    context = {
        "page": "teens",
        "title": "Earn Money as a Teen in India | Funngro for Teens",
        "skill_categories": [
            {"icon": "✍️", "name": "Writing",
             "desc": "Blog posts, captions, product descriptions, short stories",
             "pay_range": "₹150 – ₹500", "style": "sc--writing"},
            {"icon": "🎨", "name": "Design",
             "desc": "Canva graphics, thumbnails, flyers, basic illustrations",
             "pay_range": "₹200 – ₹700", "style": "sc--design"},
            {"icon": "📊", "name": "Research",
             "desc": "Web research, data entry, competitor lookups, spreadsheets",
             "pay_range": "₹100 – ₹350", "style": "sc--data"},
            {"icon": "📱", "name": "Social Media",
             "desc": "Hashtag research, engagement tracking, caption packs",
             "pay_range": "₹150 – ₹400", "style": "sc--social"},
            {"icon": "💻", "name": "Tech Tasks",
             "desc": "App testing, website feedback, basic coding, form building",
             "pay_range": "₹200 – ₹800", "style": "sc--tech"},
            {"icon": "🎬", "name": "Video & Audio",
             "desc": "Subtitles, video reviews, script writing, voiceover scripts",
             "pay_range": "₹180 – ₹600", "style": "sc--video"},
        ],
        "teen_stories": [
            {
                "name": "Priya", "age": 17, "city": "Mumbai", "skill": "Writing",
                "earned": "₹8,400", "tasks": 42, "rating": 4.9,
                "quote": "I started on Funngro during summer break and made enough to buy my own laptop.",
                "initial": "P", "gradient": "linear-gradient(135deg,#FF6B6B,#ff9a5c)",
            },
            {
                "name": "Mihir", "age": 16, "city": "Pune", "skill": "Design",
                "earned": "₹6,100", "tasks": 28, "rating": 5.0,
                "quote": "Canva was just a hobby for me. Now I get paid for it every weekend.",
                "initial": "M", "gradient": "linear-gradient(135deg,#6C63FF,#8b5cf6)",
            },
            {
                "name": "Sneha", "age": 15, "city": "Bangalore", "skill": "Research",
                "earned": "₹4,750", "tasks": 19, "rating": 4.8,
                "quote": "I do research tasks between study sessions. The skills are the real win.",
                "initial": "S", "gradient": "linear-gradient(135deg,#00C37A,#0ea5e9)",
            },
        ],
        "how_steps": [
            {"num": 1, "title": "Create your profile",
             "desc": "Tell us your age, skills, and interests. Takes 5 minutes. No CV needed."},
            {"num": 2, "title": "Pick a task",
             "desc": "Browse tasks that match your skills. Apply with a short note about why you're a good fit."},
            {"num": 3, "title": "Do the work",
             "desc": "Complete the task at your own pace within the deadline. Ask questions if unsure."},
            {"num": 4, "title": "Get paid 💸",
             "desc": "Company approves your work → money lands in your account. Simple as that."},
        ],
    }
    return render_template("teens.html", **context)


@app.route("/contact", methods=["POST"])
def contact():
    """
    Handle contact / sign-up form submissions.
    Accepts both JSON (fetch) and form POST.
    Returns JSON response.
    """
    # Support both JSON and form data
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    name  = data.get("name", "").strip()
    email = data.get("email", "").strip()
    msg   = data.get("message", "").strip()
    source = data.get("source", "general")   # "company" | "teens" | "general"

    # ── Validation ──
    errors = {}
    if not name or len(name) < 2:
        errors["name"] = "Please enter your full name."
    if not email or not is_valid_email(email):
        errors["email"] = "Please enter a valid email address."

    if errors:
        return jsonify({"success": False, "errors": errors}), 422

    # ── Save submission ──
    submission = {
        "id": len(contact_submissions) + 1,
        "name": name,
        "email": email,
        "message": msg,
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
    }
    contact_submissions.append(submission)

    # ── Log to console (replace with email/DB in production) ──
    app.logger.info(f"[Contact] #{submission['id']} — {name} <{email}> (source: {source})")

    return jsonify({
        "success": True,
        "message": f"Thanks {name}! We'll get back to you at {email} within 24 hours.",
    }), 200


@app.route("/api/stats")
def api_stats():
    """Public API — platform statistics (used by frontend JS if needed)."""
    return jsonify({
        "total_teens": 12483,
        "completion_rate": 98.2,
        "avg_first_submission_hours": 4,
        "tasks_completed_today": 341,
        "top_categories": ["Writing", "Design", "Research"],
    })


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return render_template("500.html"), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)