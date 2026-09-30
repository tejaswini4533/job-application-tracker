import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Resume

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")

ALLOWED = {"pdf", "doc", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@resumes_bp.route("/")
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return render_template("resumes/index.html", resumes=resumes)


@resumes_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("resume")
    if not file or file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("resumes.index"))
    if not allowed_file(file.filename):
        flash("Only PDF, DOC, and DOCX files are allowed.", "danger")
        return redirect(url_for("resumes.index"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name))

    resume = Resume(user_id=current_user.id, filename=safe_name, original_name=file.filename)
    db.session.add(resume)
    db.session.commit()
    flash("Resume uploaded successfully.", "success")
    return redirect(url_for("resumes.index"))


@resumes_bp.route("/<int:resume_id>/download")
@login_required
def download(resume_id):
    resume = db.get_or_404(Resume, resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], resume.filename,
                               as_attachment=True, download_name=resume.original_name)


@resumes_bp.post("/<int:resume_id>/delete")
@login_required
def delete(resume_id):
    resume = db.get_or_404(Resume, resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], resume.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted.", "success")
    return redirect(url_for("resumes.index"))
