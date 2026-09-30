from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Application, Interview, INTERVIEW_TYPES, INTERVIEW_ROUNDS, INTERVIEW_RESULTS

interviews_bp = Blueprint("interviews", __name__, url_prefix="/interviews")


def _own_app_or_404(app_id):
    a = db.get_or_404(Application, app_id)
    if a.user_id != current_user.id:
        abort(403)
    return a


def _own_interview_or_404(interview_id):
    iv = db.get_or_404(Interview, interview_id)
    if iv.application.user_id != current_user.id:
        abort(403)
    return iv


@interviews_bp.route("/")
@login_required
def index():
    today = date.today()
    upcoming = (
        Interview.query
        .join(Application)
        .filter(Application.user_id == current_user.id, Interview.interview_date >= today, Interview.result == "Pending")
        .order_by(Interview.interview_date.asc())
        .all()
    )
    past = (
        Interview.query
        .join(Application)
        .filter(Application.user_id == current_user.id,
                db.or_(Interview.interview_date < today, Interview.result != "Pending"))
        .order_by(Interview.interview_date.desc())
        .limit(30)
        .all()
    )
    return render_template("interviews/index.html", upcoming=upcoming, past=past, today=today)


@interviews_bp.route("/add/<int:app_id>", methods=["GET", "POST"])
@login_required
def add(app_id):
    application = _own_app_or_404(app_id)
    if request.method == "POST":
        iv = Interview(
            application_id=app_id,
            interview_date=date.fromisoformat(request.form["interview_date"]),
            interview_time=request.form.get("interview_time", "").strip(),
            interview_type=request.form.get("interview_type", "Video Call"),
            interview_round=request.form.get("interview_round", "Round 1"),
            location_or_link=request.form.get("location_or_link", "").strip(),
            notes=request.form.get("notes", "").strip(),
            result=request.form.get("result", "Pending"),
        )
        db.session.add(iv)
        if application.status not in ["Interview", "Offer"]:
            application.status = "Interview"
        db.session.commit()
        flash("Interview added.", "success")
        return redirect(url_for("applications.detail", app_id=app_id))

    return render_template("interviews/form.html", application=application, interview=None,
                           INTERVIEW_TYPES=INTERVIEW_TYPES, INTERVIEW_ROUNDS=INTERVIEW_ROUNDS,
                           INTERVIEW_RESULTS=INTERVIEW_RESULTS)


@interviews_bp.route("/<int:interview_id>/edit", methods=["GET", "POST"])
@login_required
def edit(interview_id):
    iv = _own_interview_or_404(interview_id)
    if request.method == "POST":
        iv.interview_date = date.fromisoformat(request.form["interview_date"])
        iv.interview_time = request.form.get("interview_time", "").strip()
        iv.interview_type = request.form.get("interview_type", "Video Call")
        iv.interview_round = request.form.get("interview_round", "Round 1")
        iv.location_or_link = request.form.get("location_or_link", "").strip()
        iv.notes = request.form.get("notes", "").strip()
        iv.result = request.form.get("result", "Pending")
        db.session.commit()
        flash("Interview updated.", "success")
        return redirect(url_for("applications.detail", app_id=iv.application_id))

    return render_template("interviews/form.html", application=iv.application, interview=iv,
                           INTERVIEW_TYPES=INTERVIEW_TYPES, INTERVIEW_ROUNDS=INTERVIEW_ROUNDS,
                           INTERVIEW_RESULTS=INTERVIEW_RESULTS)


@interviews_bp.post("/<int:interview_id>/delete")
@login_required
def delete(interview_id):
    iv = _own_interview_or_404(interview_id)
    app_id = iv.application_id
    db.session.delete(iv)
    db.session.commit()
    flash("Interview deleted.", "success")
    return redirect(url_for("applications.detail", app_id=app_id))
