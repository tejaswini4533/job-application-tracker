"""
seed_demo.py — Creates a demo user and sample applications for testing.
Run once: python seed_demo.py
"""
from app import create_app, db
from app.models import User, Application, Interview
from datetime import date, timedelta

app = create_app()

with app.app_context():
    # Skip if demo user already exists
    if User.query.filter_by(email="demo@jobtrack.com").first():
        print("Demo user already exists. Skipping seed.")
    else:
        user = User(name="Demo User", email="demo@jobtrack.com")
        user.set_password("demo1234")
        db.session.add(user)
        db.session.flush()

        today = date.today()
        apps_data = [
            ("Google", "Software Engineer", "Bangalore", "Full-time", "LinkedIn", "Interview", today - timedelta(days=10)),
            ("Microsoft", "Backend Developer", "Hyderabad", "Full-time", "Referral", "Offer", today - timedelta(days=20)),
            ("Amazon", "SDE-1", "Remote", "Full-time", "Company Website", "Shortlisted", today - timedelta(days=5)),
            ("Flipkart", "Data Engineer", "Bangalore", "Full-time", "Naukri", "Applied", today - timedelta(days=3)),
            ("Infosys", "Systems Engineer", "Pune", "Full-time", "College Placement", "Rejected", today - timedelta(days=30)),
            ("Swiggy", "Frontend Developer", "Bangalore", "Full-time", "LinkedIn", "Applied", today - timedelta(days=1)),
            ("Razorpay", "Full Stack Developer", "Remote", "Full-time", "Indeed", "Saved", today),
        ]

        for company, role, location, jtype, source, status, applied in apps_data:
            a = Application(
                user_id=user.id,
                company=company, role=role, location=location,
                job_type=jtype, source=source, status=status,
                applied_date=applied,
                follow_up_date=applied + timedelta(days=7) if status == "Applied" else None,
            )
            db.session.add(a)

        db.session.commit()
        print("Demo user created: demo@jobtrack.com / demo1234")
        print(f"Added {len(apps_data)} sample applications.")
