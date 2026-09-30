from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import Application, Resume, STATUSES, JOB_TYPES, SOURCES

apps_bp = Blueprint("applications", __name__, url_prefix="/applications")

ITEMS_PER_PAGE = 10


def _own_or_404(app_id):
    a = db.get_or_404(Application, app_id)
    if a.user_id != current_user.id:
        abort(403)
    return a


@apps_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    job_type = request.args.get("job_type", "")
    sort = request.args.get("sort", "newest")
    page = request.args.get("page", 1, type=int)

    query = Application.query.filter_by(user_id=current_user.id)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Application.company.ilike(like),
            Application.role.ilike(like),
            Application.location.ilike(like),
        ))
    if status:
        query = query.filter_by(status=status)
    if job_type:
        query = query.filter_by(job_type=job_type)

    if sort == "oldest":
        query = query.order_by(Application.applied_date.asc())
    elif sort == "company":
        query = query.order_by(Application.company.asc())
    elif sort == "status":
        query = query.order_by(Application.status.asc())
    else:
        query = query.order_by(Application.applied_date.desc(), Application.id.desc())

    pagination = query.paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)

    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "applications/index.html",
        pagination=pagination,
        applications=pagination.items,
        q=q, selected_status=status, selected_job_type=job_type, sort=sort,
        STATUSES=STATUSES, JOB_TYPES=JOB_TYPES,
        resumes=resumes,
    )


@apps_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        resume_id = request.form.get("resume_id") or None
        if resume_id:
            resume = db.session.get(Resume, int(resume_id))
            if not resume or resume.user_id != current_user.id:
                resume_id = None

        app_obj = Application(
            user_id=current_user.id,
            company=request.form["company"].strip(),
            role=request.form["role"].strip(),
            location=request.form.get("location", "").strip(),
            job_type=request.form.get("job_type", "Full-time"),
            source=request.form.get("source", "Other"),
            applied_date=date.fromisoformat(request.form.get("applied_date") or date.today().isoformat()),
            status=request.form.get("status", "Applied"),
            salary=request.form.get("salary", "").strip(),
            job_url=request.form.get("job_url", "").strip(),
            contact_name=request.form.get("contact_name", "").strip(),
            contact_email=request.form.get("contact_email", "").strip(),
            notes=request.form.get("notes", "").strip(),
            follow_up_date=date.fromisoformat(request.form["follow_up_date"]) if request.form.get("follow_up_date") else None,
            follow_up_notes=request.form.get("follow_up_notes", "").strip(),
            resume_id=resume_id,
        )
        db.session.add(app_obj)
        db.session.commit()
        flash("Application added successfully.", "success")
        return redirect(url_for("applications.index"))

    return render_template("applications/form.html", application=None, title="Add Application",
                           STATUSES=STATUSES, JOB_TYPES=JOB_TYPES, SOURCES=SOURCES, resumes=resumes)


@apps_bp.route("/<int:app_id>")
@login_required
def detail(app_id):
    application = _own_or_404(app_id)
    interviews = application.interviews.order_by(db.text("interview_date desc")).all()
    return render_template("applications/detail.html", application=application,
                           interviews=interviews, STATUSES=STATUSES)


@apps_bp.route("/<int:app_id>/edit", methods=["GET", "POST"])
@login_required
def edit(app_id):
    application = _own_or_404(app_id)
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        resume_id = request.form.get("resume_id") or None
        if resume_id:
            resume = db.session.get(Resume, int(resume_id))
            if not resume or resume.user_id != current_user.id:
                resume_id = None

        application.company = request.form["company"].strip()
        application.role = request.form["role"].strip()
        application.location = request.form.get("location", "").strip()
        application.job_type = request.form.get("job_type", "Full-time")
        application.source = request.form.get("source", "Other")
        application.applied_date = date.fromisoformat(request.form.get("applied_date") or date.today().isoformat())
        application.status = request.form.get("status", "Applied")
        application.salary = request.form.get("salary", "").strip()
        application.job_url = request.form.get("job_url", "").strip()
        application.contact_name = request.form.get("contact_name", "").strip()
        application.contact_email = request.form.get("contact_email", "").strip()
        application.notes = request.form.get("notes", "").strip()
        application.follow_up_date = date.fromisoformat(request.form["follow_up_date"]) if request.form.get("follow_up_date") else None
        application.follow_up_notes = request.form.get("follow_up_notes", "").strip()
        application.follow_up_done = request.form.get("follow_up_done") == "on"
        application.resume_id = resume_id
        db.session.commit()
        flash("Application updated.", "success")
        return redirect(url_for("applications.detail", app_id=app_id))

    return render_template("applications/form.html", application=application, title="Edit Application",
                           STATUSES=STATUSES, JOB_TYPES=JOB_TYPES, SOURCES=SOURCES, resumes=resumes)


@apps_bp.post("/<int:app_id>/delete")
@login_required
def delete(app_id):
    application = _own_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    flash("Application deleted.", "success")
    return redirect(url_for("applications.index"))


@apps_bp.post("/<int:app_id>/status")
@login_required
def update_status(app_id):
    application = _own_or_404(app_id)
    new_status = request.form.get("status")
    if new_status in STATUSES:
        application.status = new_status
        db.session.commit()
        flash(f"Status updated to {new_status}.", "success")
    return redirect(request.referrer or url_for("applications.index"))


@apps_bp.route("/api/list")
@login_required
def api_list():
    apps = Application.query.filter_by(user_id=current_user.id).order_by(Application.id.desc()).all()
    return jsonify([a.to_dict() for a in apps])
