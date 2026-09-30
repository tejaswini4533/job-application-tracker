from datetime import date, datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    resumes = db.relationship("Resume", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


STATUSES = ["Saved", "Applied", "Shortlisted", "Interview", "Offer", "Rejected"]
JOB_TYPES = ["Full-time", "Internship", "Part-time", "Contract", "Freelance"]
SOURCES = ["LinkedIn", "Naukri", "Company Website", "Internshala", "College Placement", "Referral", "Indeed", "Other"]
INTERVIEW_TYPES = ["Phone Screen", "Video Call", "On-site", "Technical", "HR Round", "Group Discussion", "Other"]
INTERVIEW_ROUNDS = ["Round 1", "Round 2", "Round 3", "Final Round", "HR Round", "Other"]
INTERVIEW_RESULTS = ["Pending", "Passed", "Failed", "No Show", "Cancelled"]


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
    follow_up_date = db.Column(db.Date, nullable=True)
    follow_up_notes = db.Column(db.Text, default="")
    follow_up_done = db.Column(db.Boolean, default=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interviews = db.relationship("Interview", backref="application", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_follow_up_overdue(self):
        if self.follow_up_date and not self.follow_up_done:
            return self.follow_up_date < date.today()
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "location": self.location,
            "job_type": self.job_type,
            "source": self.source,
            "applied_date": self.applied_date.isoformat() if self.applied_date else "",
            "status": self.status,
            "salary": self.salary,
            "job_url": self.job_url,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }


class Interview(db.Model):
    __tablename__ = "interviews"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.String(10), default="")
    interview_type = db.Column(db.String(80), default="Video Call")
    interview_round = db.Column(db.String(80), default="Round 1")
    location_or_link = db.Column(db.String(500), default="")
    notes = db.Column(db.Text, default="")
    result = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_upcoming(self):
        return self.interview_date >= date.today() and self.result == "Pending"

    @property
    def company(self):
        return self.application.company

    @property
    def role(self):
        return self.application.role


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="resume", lazy="dynamic")
