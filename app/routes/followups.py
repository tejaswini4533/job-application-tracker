from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Application

followups_bp = Blueprint("followups", __name__, url_prefix="/followups")


@followups_bp.route("/")
@login_required
def index():
    today = date.today()
    all_apps = Application.query.filter_by(user_id=current_user.id).all()
    pending = [a for a in all_apps if a.follow_up_date and not a.follow_up_done and a.follow_up_date >= today]
    overdue = [a for a in all_apps if a.follow_up_date and not a.follow_up_done and a.follow_up_date < today]
    done = [a for a in all_apps if a.follow_up_done]
    pending.sort(key=lambda a: a.follow_up_date)
    overdue.sort(key=lambda a: a.follow_up_date)
    return render_template("followups/index.html", pending=pending, overdue=overdue, done=done, today=today)


@followups_bp.post("/<int:app_id>/complete")
@login_required
def complete(app_id):
    a = db.get_or_404(Application, app_id)
    if a.user_id != current_user.id:
        abort(403)
    a.follow_up_done = True
    db.session.commit()
    flash("Follow-up marked as completed.", "success")
    return redirect(url_for("followups.index"))


@followups_bp.post("/<int:app_id>/reopen")
@login_required
def reopen(app_id):
    a = db.get_or_404(Application, app_id)
    if a.user_id != current_user.id:
        abort(403)
    a.follow_up_done = False
    db.session.commit()
    flash("Follow-up reopened.", "info")
    return redirect(url_for("followups.index"))
