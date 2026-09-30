
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "job-tracker-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "job_tracker.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(120), default="")
    job_type = db.Column(db.String(50), default="Full-time")
    source = db.Column(db.String(80), default="Other")
    applied_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(50), default="Applied")
    salary = db.Column(db.String(80), default="")
    job_url = db.Column(db.String(500), default="")
    contact_name = db.Column(db.String(120), default="")
    contact_email = db.Column(db.String(150), default="")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id, "company": self.company, "role": self.role,
            "location": self.location, "job_type": self.job_type,
            "source": self.source,
            "applied_date": self.applied_date.isoformat() if self.applied_date else "",
            "status": self.status, "salary": self.salary,
            "job_url": self.job_url, "contact_name": self.contact_name,
            "contact_email": self.contact_email, "notes": self.notes
        }

STATUSES = ["Applied", "Screening", "Interview", "Assessment", "Offer", "Rejected", "Withdrawn"]

@app.context_processor
def inject_globals():
    return {"STATUSES": STATUSES}

@app.route("/")
def dashboard():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    sort = request.args.get("sort", "newest")

    query = JobApplication.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            JobApplication.company.ilike(like),
            JobApplication.role.ilike(like),
            JobApplication.location.ilike(like),
            JobApplication.notes.ilike(like)
        ))
    if status:
        query = query.filter_by(status=status)

    if sort == "oldest":
        query = query.order_by(JobApplication.applied_date.asc())
    elif sort == "company":
        query = query.order_by(JobApplication.company.asc())
    else:
        query = query.order_by(JobApplication.applied_date.desc(), JobApplication.id.desc())

    applications = query.all()

    all_apps = JobApplication.query.all()
    stats = {
        "total": len(all_apps),
        "active": sum(a.status not in ["Rejected", "Withdrawn", "Offer"] for a in all_apps),
        "interviews": sum(a.status == "Interview" for a in all_apps),
        "offers": sum(a.status == "Offer" for a in all_apps),
        "rejected": sum(a.status == "Rejected" for a in all_apps),
    }

    status_counts = {s: sum(a.status == s for a in all_apps) for s in STATUSES}
    return render_template("dashboard.html", applications=applications, stats=stats,
                           status_counts=status_counts, q=q, selected_status=status, sort=sort)

@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        app_obj = JobApplication(
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
            notes=request.form.get("notes", "").strip()
        )
        db.session.add(app_obj)
        db.session.commit()
        flash("Application added successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", application=None, title="Add Application")

@app.route("/edit/<int:app_id>", methods=["GET", "POST"])
def edit_application(app_id):
    application = db.get_or_404(JobApplication, app_id)
    if request.method == "POST":
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
        db.session.commit()
        flash("Application updated.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", application=application, title="Edit Application")

@app.post("/delete/<int:app_id>")
def delete_application(app_id):
    application = db.get_or_404(JobApplication, app_id)
    db.session.delete(application)
    db.session.commit()
    flash("Application deleted.", "success")
    return redirect(url_for("dashboard"))

@app.post("/status/<int:app_id>")
def update_status(app_id):
    application = db.get_or_404(JobApplication, app_id)
    new_status = request.form.get("status")
    if new_status in STATUSES:
        application.status = new_status
        db.session.commit()
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/api/applications")
def api_applications():
    return jsonify([a.to_dict() for a in JobApplication.query.order_by(JobApplication.id.desc()).all()])

@app.route("/api/stats")
def api_stats():
    all_apps = JobApplication.query.all()
    return jsonify({
        "total": len(all_apps),
        "interviews": sum(a.status == "Interview" for a in all_apps),
        "offers": sum(a.status == "Offer" for a in all_apps),
        "rejected": sum(a.status == "Rejected" for a in all_apps),
        "by_status": {s: sum(a.status == s for a in all_apps) for s in STATUSES}
    })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
