from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Application, Interview, STATUSES, SOURCES

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    all_apps = Application.query.filter_by(user_id=current_user.id).all()
    stats = {s: sum(a.status == s for a in all_apps) for s in STATUSES}
    stats["total"] = len(all_apps)

    today = date.today()
    upcoming_interviews = (
        Interview.query.join(Application)
        .filter(
            Application.user_id == current_user.id,
            Interview.interview_date >= today,
            Interview.result == "Pending",
        )
        .order_by(Interview.interview_date.asc())
        .limit(5)
        .all()
    )

    overdue_followups = [
        a for a in all_apps
        if a.follow_up_date and not a.follow_up_done and a.follow_up_date < today
    ]

    recent_apps = (
        Application.query.filter_by(user_id=current_user.id)
        .order_by(Application.created_at.desc())
        .limit(8)
        .all()
    )

    monthly_data = []
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        count = sum(
            1 for a in all_apps
            if a.applied_date
            and a.applied_date.year == month_date.year
            and a.applied_date.month == month_date.month
        )
        monthly_data.append({"month": month_date.strftime("%b %Y"), "count": count})

    return render_template(
        "dashboard.html",
        stats=stats,
        upcoming_interviews=upcoming_interviews,
        overdue_followups=overdue_followups,
        recent_apps=recent_apps,
        monthly_data=monthly_data,
        STATUSES=STATUSES,
        today=today,
    )


@main_bp.route("/analytics")
@login_required
def analytics():
    all_apps = Application.query.filter_by(user_id=current_user.id).all()
    today = date.today()

    stats = {s: sum(a.status == s for a in all_apps) for s in STATUSES}
    stats["total"] = len(all_apps)

    responded = sum(a.status in ["Shortlisted", "Interview", "Offer", "Rejected"] for a in all_apps)
    stats["response_rate"] = round((responded / len(all_apps) * 100) if all_apps else 0, 1)
    stats["interview_rate"] = round((stats.get("Interview", 0) / len(all_apps) * 100) if all_apps else 0, 1)
    stats["offer_rate"] = round((stats.get("Offer", 0) / len(all_apps) * 100) if all_apps else 0, 1)
    stats["rejection_rate"] = round((stats.get("Rejected", 0) / len(all_apps) * 100) if all_apps else 0, 1)

    monthly_data = []
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        count = sum(
            1 for a in all_apps
            if a.applied_date
            and a.applied_date.year == month_date.year
            and a.applied_date.month == month_date.month
        )
        monthly_data.append({"month": month_date.strftime("%b %Y"), "count": count})

    source_data = {s: sum(a.source == s for a in all_apps) for s in SOURCES}

    company_counts = {}
    for a in all_apps:
        company_counts[a.company] = company_counts.get(a.company, 0) + 1
    top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    return render_template(
        "analytics.html",
        stats=stats,
        monthly_data=monthly_data,
        source_data=source_data,
        top_companies=top_companies,
        STATUSES=STATUSES,
        SOURCES=SOURCES,
    )


@main_bp.route("/search")
@login_required
def search():
    """Global search — redirects to applications page with query."""
    q = request.args.get("q", "").strip()
    return redirect(url_for("applications.index", q=q))


@main_bp.route("/api/stats")
@login_required
def api_stats():
    all_apps = Application.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "total": len(all_apps),
        "by_status": {s: sum(a.status == s for a in all_apps) for s in STATUSES},
    })


@main_bp.route("/api/notifications")
@login_required
def api_notifications():
    """Returns real notification counts for the bell icon."""
    today = date.today()
    all_apps = Application.query.filter_by(user_id=current_user.id).all()

    overdue_count = sum(
        1 for a in all_apps
        if a.follow_up_date and not a.follow_up_done and a.follow_up_date < today
    )
    upcoming_interviews = (
        Interview.query.join(Application)
        .filter(
            Application.user_id == current_user.id,
            Interview.interview_date >= today,
            Interview.interview_date <= today + timedelta(days=2),
            Interview.result == "Pending",
        )
        .all()
    )

    notifications = []
    for iv in upcoming_interviews:
        days = (iv.interview_date - today).days
        label = "Today" if days == 0 else "Tomorrow" if days == 1 else "In 2 days"
        notifications.append({
            "type": "interview",
            "title": f"Interview {label}",
            "body": f"{iv.company} — {iv.interview_type}",
            "url": url_for("interviews.index"),
        })

    if overdue_count:
        notifications.append({
            "type": "followup",
            "title": f"{overdue_count} Overdue Follow-up{'s' if overdue_count > 1 else ''}",
            "body": "You have follow-ups that need attention.",
            "url": url_for("followups.index"),
        })

    return jsonify({"count": len(notifications), "items": notifications})
