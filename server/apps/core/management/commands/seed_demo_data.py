import os
from datetime import timedelta
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.applications.models import Application, ApplicationStatusHistory
from apps.candidates.models import CandidateCV, CandidateProfile, CandidateSkill, Experience, Skill
from apps.companies.models import Company
from apps.jobs.models import Category, Job

REFERENCE_CATEGORIES = [("Software Engineering", "software-engineering"), ("Web Development", "web-development"), ("Mobile Development", "mobile-development"), ("AI / Machine Learning", "ai-machine-learning"), ("Data Engineering / Analytics", "data-engineering-analytics"), ("Cybersecurity", "cybersecurity"), ("DevOps / Cloud", "devops-cloud"), ("IT Support / Systems", "it-support-systems"), ("UI/UX Design", "ui-ux-design"), ("Product / Project Management", "product-project-management"), ("Business / Marketing", "business-marketing"), ("Finance / Accounting", "finance-accounting"), ("Human Resources", "human-resources"), ("Sales / Customer Service", "sales-customer-service")]
REFERENCE_SKILLS = ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Go", "Kotlin", "Swift", "SQL", "HTML", "CSS", "React", "Vue.js", "Angular", "Responsive Design", "Accessibility", "Django", "Django REST Framework", "FastAPI", "Node.js", "Express.js", "REST API", "GraphQL", "PostgreSQL", "MySQL", "SQLite", "Redis", "MongoDB", "Git", "Docker", "Linux", "CI/CD", "GitHub Actions", "AWS", "Azure", "Kubernetes", "Pandas", "NumPy", "Data Analysis", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Unit Testing", "Integration Testing", "Pytest", "Jest", "Playwright", "OWASP", "Application Security", "Communication", "Teamwork", "Problem Solving", "Critical Thinking", "Project Management", "English Communication"]


class Command(BaseCommand):
    help = "Create or update deterministic demo records without deleting user data."

    def add_arguments(self, parser):
        parser.add_argument("--password", dest="password", help="Password for demo users; otherwise DEMO_PASSWORD is required.")
        parser.add_argument("--no-application", action="store_true", help="Skip the sample candidate application.")

    @transaction.atomic
    def handle(self, *args, **options):
        password = options.get("password") or os.getenv("DEMO_PASSWORD")
        if not password or len(password) < 8:
            raise CommandError("Provide --password or DEMO_PASSWORD (at least 8 characters).")

        categories = {}
        created_categories = 0
        for name, slug in REFERENCE_CATEGORIES:
            category, created = Category.objects.update_or_create(slug=slug, defaults={"name": name, "is_active": True})
            categories[slug] = category
            created_categories += int(created)
        skills = {}
        created_skills = 0
        for name in REFERENCE_SKILLS:
            skill, created = Skill.objects.get_or_create(name=name, defaults={"is_active": True})
            if not skill.is_active:
                skill.is_active = True
                skill.save(update_fields=["is_active"])
            skills[name] = skill
            created_skills += int(created)

        candidate, created = User.objects.get_or_create(
            email="demo.candidate@example.com",
            defaults={"first_name": "Demo", "last_name": "Candidate", "role": User.Role.CANDIDATE},
        )
        if created:
            candidate.set_password(password)
            candidate.save(update_fields=["password"])
        elif candidate.role != User.Role.CANDIDATE:
            raise CommandError("demo.candidate@example.com exists with a different role.")
        candidate_profile, _ = CandidateProfile.objects.get_or_create(
            user=candidate,
            defaults={"full_name": "Demo Candidate", "location": "Hanoi", "summary": "Seeded candidate profile."},
        )
        for skill_name in ("Python", "Django", "PostgreSQL", "Communication"):
            CandidateSkill.objects.get_or_create(candidate=candidate_profile, skill=skills[skill_name])
        Experience.objects.get_or_create(candidate=candidate_profile, company_name="PTIT CareerHub Lab", job_title="Backend Intern", defaults={"description": "Built REST APIs and automated tests.", "start_date": timezone.localdate() - timedelta(days=240), "end_date": timezone.localdate() - timedelta(days=30), "is_current": False})

        employer, created = User.objects.get_or_create(
            email="demo.employer@example.com",
            defaults={"first_name": "Demo", "last_name": "Employer", "role": User.Role.EMPLOYER},
        )
        if created:
            employer.set_password(password)
            employer.save(update_fields=["password"])
        elif employer.role != User.Role.EMPLOYER:
            raise CommandError("demo.employer@example.com exists with a different role.")
        company, _ = Company.objects.get_or_create(
            owner=employer,
            defaults={"name": "CareerHub Demo Company", "website": "https://example.com", "address": "Hanoi", "description": "Seeded demo employer."},
        )
        category = categories["software-engineering"]

        deadline = timezone.localdate() + timedelta(days=30)
        published, _ = Job.objects.get_or_create(
            company=company,
            title="Demo Backend Engineer",
            defaults={
                "category": category, "created_by": employer, "description": "Build recruitment platform APIs.",
                "requirements": "Python, Django, PostgreSQL", "location": "Hanoi", "employment_type": Job.EmploymentType.FULL_TIME,
                "salary_min": 15000000, "salary_max": 30000000, "salary_currency": "VND", "deadline": deadline,
                "status": Job.Status.PUBLISHED, "published_at": timezone.now(),
            },
        )
        if published.status != Job.Status.PUBLISHED:
            published.category = category
            published.status = Job.Status.PUBLISHED
            published.deadline = deadline
            published.published_at = published.published_at or timezone.now()
            published.save(update_fields=["category", "status", "deadline", "published_at", "updated_at"])

        pending, _ = Job.objects.get_or_create(
            company=company,
            title="Demo Frontend Engineer (Review)",
            defaults={
                "category": category, "created_by": employer, "description": "Frontend role awaiting moderation.",
                "requirements": "React, TypeScript\nResponsive UI implementation\nCode review collaboration",
                "benefits": "Flexible remote work\nLearning budget\nMentorship from senior engineers",
                "location": "Remote", "employment_type": Job.EmploymentType.FULL_TIME, "deadline": deadline,
                "status": Job.Status.PENDING,
            },
        )
        # Keep an existing demo row useful after the seed schema/content evolves.
        pending_updates = []
        if not pending.description:
            pending.description = "Frontend role awaiting moderation."
            pending_updates.append("description")
        if not pending.requirements:
            pending.requirements = "React, TypeScript\nResponsive UI implementation\nCode review collaboration"
            pending_updates.append("requirements")
        if not pending.benefits:
            pending.benefits = "Flexible remote work\nLearning budget\nMentorship from senior engineers"
            pending_updates.append("benefits")
        if pending_updates:
            pending_updates.append("updated_at")
            pending.save(update_fields=pending_updates)
        if pending.status not in {Job.Status.PENDING, Job.Status.PUBLISHED}:
            pending.status = Job.Status.PENDING
            pending.save(update_fields=["status", "updated_at"])

        application = None
        if not options["no_application"]:
            cv = CandidateCV.objects.filter(candidate=candidate_profile, status=CandidateCV.Status.ACTIVE).first()
            if cv is None:
                cv = CandidateCV.objects.create(
                    candidate=candidate_profile,
                    file=ContentFile(b"%PDF-1.4\n%%EOF\n", name="demo-candidate.pdf"),
                    original_filename="demo-candidate.pdf",
                    file_size=15,
                    content_type="application/pdf",
                )
            application, app_created = Application.objects.get_or_create(
                job=published, candidate=candidate_profile,
                defaults={"cv": cv, "cover_letter": "Demo application for integration testing."},
            )
            if app_created:
                ApplicationStatusHistory.objects.create(
                    application=application, previous_status="", new_status=application.status,
                    changed_by=candidate, note="Seeded demo application",
                )

        self.stdout.write(self.style.SUCCESS("Demo and reference data are ready (idempotent)."))
        self.stdout.write(f"categories_created={created_categories} skills_created={created_skills} category_count={Category.objects.count()} skill_count={Skill.objects.count()}")
        self.stdout.write(f"candidate=demo.candidate@example.com employer=demo.employer@example.com company_id={company.id} published_job_id={published.id} pending_job_id={pending.id}")
        if application:
            self.stdout.write(f"application_id={application.id}")
