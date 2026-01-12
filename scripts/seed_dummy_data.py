import argparse
import sys
from pathlib import Path
import random
from datetime import datetime, timezone

from sqlmodel import Session, select

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from db import engine
from models import (
    Course,
    CourseClassification,
    CourseDurationUnit,
    CourseEnrollment,
    CourseFlag,
    CourseProvider,
    EmployeeManager,
    Notification,
    User,
)


PROVIDERS = [
    "Coursera",
    "LinkedIn Learning",
    "Udemy Business",
    "Pluralsight",
    "Internal",
    "edX",
    "Skillshare",
    "OpenSesame",
]

CLASSIFICATIONS = [
    "Leadership",
    "Technical",
    "Compliance",
    "Soft Skills",
    "Product",
    "Data",
    "Security",
    "Operations",
]

FLAGS = [
    "Featured",
    "New",
    "Popular",
    "Mandatory",
    "Optional",
    "Trending",
]

DURATION_UNITS = ["minutes", "days", "weeks", "months", "years"]

SKILLS = [
    "Communication",
    "Leadership",
    "Coaching",
    "Analytics",
    "Cybersecurity",
    "Project Management",
    "Product Thinking",
    "Stakeholder Management",
    "Critical Thinking",
    "Negotiation",
]

COMPETENCIES = [
    "L&D Fundamentals",
    "People Management",
    "Data Literacy",
    "Compliance",
    "Strategic Planning",
    "Operational Excellence",
    "Customer Focus",
]

TOPICS = [
    "Inclusive Communication",
    "Remote Coaching",
    "Security Awareness",
    "Data Literacy",
    "Leadership Foundations",
    "Product Strategy",
    "Negotiation Mastery",
    "Time Management",
    "Conflict Resolution",
    "Agile Delivery",
    "Stakeholder Alignment",
    "Customer Empathy",
    "Presentation Skills",
    "Design Thinking",
    "Quality Management",
    "Compliance Essentials",
]

ADJECTIVES = [
    "Advanced",
    "Practical",
    "Modern",
    "Essential",
    "Foundational",
    "Strategic",
    "Hands-on",
    "Executive",
    "High-Impact",
]


def get_or_create_by_name(session: Session, model, name: str):
    existing = session.exec(select(model).where(model.name == name)).first()
    if existing:
        return existing
    obj = model(name=name)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("  ", " ")
        .replace(" ", "-")
    )


def seed_courses(session: Session, target_count: int, manager_id: int | None):
    provider_map = {p: get_or_create_by_name(session, CourseProvider, p) for p in PROVIDERS}
    classification_map = {
        c: get_or_create_by_name(session, CourseClassification, c) for c in CLASSIFICATIONS
    }
    flag_map = {f: get_or_create_by_name(session, CourseFlag, f) for f in FLAGS}
    unit_map = {u: get_or_create_by_name(session, CourseDurationUnit, u) for u in DURATION_UNITS}

    existing_courses = session.exec(select(Course)).all()
    existing_names = {c.name for c in existing_courses}
    courses_needed = max(target_count - len(existing_courses), 0)

    if courses_needed == 0:
        return

    random.seed(7)
    for idx in range(courses_needed):
        topic = random.choice(TOPICS)
        adjective = random.choice(ADJECTIVES)
        name = f"{adjective} {topic} {idx + 1}"
        if name in existing_names:
            name = f"{name}X"
        existing_names.add(name)

        provider_name = random.choice(PROVIDERS)
        classification_name = random.choice(CLASSIFICATIONS)
        flag_name = random.choice(FLAGS)
        unit_name = random.choice(DURATION_UNITS)

        duration = random.choice([30, 45, 60, 90, 120, 3, 5, 8, 12])
        if unit_name in {"weeks", "months", "years"}:
            duration = random.choice([1, 2, 3, 6, 12])

        assigned_by_manager = random.choice([True, False])
        skills = random.sample(SKILLS, k=random.randint(2, 4))
        competencies = random.sample(COMPETENCIES, k=random.randint(1, 2))
        slug = slugify(name)

        course = Course(
            name=name,
            description=f"{name} course designed to build {skills[0].lower()} skills.",
            provider=provider_name,
            provider_id=provider_map[provider_name].id,
            link=f"https://example.com/courses/{slug}",
            image=f"https://picsum.photos/seed/{slug}/600/400",
            duration=duration,
            duration_unit_id=unit_map[unit_name].id,
            skills=skills,
            competencies=competencies,
            classification_id=classification_map[classification_name].id,
            flag_id=flag_map[flag_name].id,
            is_active=True,
            assigned_by_manager=assigned_by_manager,
            assigned_by_manager_id=manager_id if assigned_by_manager else None,
            attribute1=random.choice(["Level 1", "Level 2", "Level 3"]),
            attribute2=random.choice(["English", "Arabic", "French"]),
            attribute3=random.choice(["Video", "Blended", "Workshop"]),
            attribute4=random.choice(["Internal", "External"]),
            attribute5=random.choice(["Short", "Medium", "Long"]),
            attribute6=random.choice(["Self-paced", "Instructor-led"]),
            attribute7=random.choice(["Certificate", "No certificate"]),
        )
        session.add(course)

    session.commit()


def seed_enrollments_and_notifications(
    session: Session, employee: User | None, manager: User | None
):
    if not employee or not manager:
        return

    rel = session.exec(
        select(EmployeeManager).where(
            EmployeeManager.employee_id == employee.id,
            EmployeeManager.manager_id == manager.id,
        )
    ).first()
    if not rel:
        session.add(EmployeeManager(employee_id=employee.id, manager_id=manager.id))
        session.commit()

    courses = session.exec(select(Course)).all()
    random.seed(11)
    selected = random.sample(courses, k=min(30, len(courses)))

    for course in selected:
        enrollment = session.exec(
            select(CourseEnrollment).where(
                CourseEnrollment.employee_id == employee.id,
                CourseEnrollment.course_id == course.id,
            )
        ).first()
        if not enrollment:
            enrollment = CourseEnrollment(
                employee_id=employee.id,
                course_id=course.id,
            )

        approved = random.choice([True, False, False])
        if approved:
            enrollment.status = "approved"
            enrollment.approved_at = datetime.now(timezone.utc)
            enrollment.approved_by = manager.id
        else:
            enrollment.status = "pending"
            enrollment.approved_at = None
            enrollment.approved_by = None

        session.add(enrollment)
        session.commit()
        session.refresh(enrollment)

        if enrollment.status == "pending":
            existing = session.exec(
                select(Notification).where(
                    Notification.user_id == manager.id,
                    Notification.type == "enrollment_requested",
                    Notification.meta["enrollment_id"].as_integer() == enrollment.id,
                )
            ).first()
            if not existing:
                session.add(
                    Notification(
                        user_id=manager.id,
                        title="Course enrollment request",
                        body=f"{employee.name or employee.email} requested enrollment in {course.name}.",
                        type="enrollment_requested",
                        meta={
                            "employee_id": employee.id,
                            "course_id": course.id,
                            "enrollment_id": enrollment.id,
                        },
                    )
                )
        else:
            existing = session.exec(
                select(Notification).where(
                    Notification.user_id == employee.id,
                    Notification.type == "enrollment_approved",
                    Notification.meta["enrollment_id"].as_integer() == enrollment.id,
                )
            ).first()
            if not existing:
                session.add(
                    Notification(
                        user_id=employee.id,
                        title="Enrollment approved",
                        body=f"Your course enrollment was approved by {manager.name or manager.email}.",
                        type="enrollment_approved",
                        meta={
                            "course_id": course.id,
                            "enrollment_id": enrollment.id,
                            "approver_id": manager.id,
                            "approver_name": manager.name or manager.email,
                        },
                    )
                )
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--courses", type=int, default=100)
    args = parser.parse_args()

    with Session(engine) as session:
        manager = session.exec(select(User).where(User.email == "manager1@example.com")).first()
        employee = session.exec(select(User).where(User.email == "employee1@example.com")).first()

        seed_courses(session, args.courses, manager.id if manager else None)
        seed_enrollments_and_notifications(session, employee, manager)

    print("SEED COMPLETE")


if __name__ == "__main__":
    main()
