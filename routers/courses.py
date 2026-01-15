from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth.deps import get_current_user, require_employee_or_manager
from db import get_session
from models import Course, CourseEnrollment, EmployeeManager, Notification, User
from schemas import CourseOut, CourseEnrollmentOut

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("/", response_model=list[CourseOut])
def list_courses(
    session: Session = Depends(get_session),
    _user=Depends(require_employee_or_manager),
):
    stmt = select(Course).order_by(Course.id)
    return session.exec(stmt).all()


@router.post("/{course_id}/enroll", response_model=CourseEnrollmentOut, status_code=status.HTTP_201_CREATED)
def request_enrollment(
    course_id: int,
    session: Session = Depends(get_session),
    employee=Depends(require_employee_or_manager),
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = session.exec(
        select(CourseEnrollment).where(
            CourseEnrollment.employee_id == employee.id,
            CourseEnrollment.course_id == course_id,
        )
    ).first()
    if existing:
        return existing

    enrollment = CourseEnrollment(
        employee_id=employee.id,
        course_id=course_id,
        status="pending",
    )
    if employee.role == "manager":
        enrollment.status = "approved"
        enrollment.approved_at = datetime.now(timezone.utc)
        enrollment.approved_by = employee.id
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    if employee.role == "manager":
        return enrollment

    manager = session.exec(
        select(EmployeeManager).where(EmployeeManager.employee_id == employee.id)
    ).first()
    if not manager:
        raise HTTPException(status_code=400, detail="No manager assigned to this employee")

    notification = Notification(
        user_id=manager.manager_id,
        title="Course enrollment request",
        body=f"{employee.name or employee.email} requested enrollment in {course.name}.",
        type="enrollment_requested",
        meta={"employee_id": employee.id, "course_id": course_id, "enrollment_id": enrollment.id},
    )
    session.add(notification)
    session.commit()

    return enrollment
@router.post("/{course_id}/assign", response_model=CourseOut)
def toggle_assignment(
    course_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role != "manager" and user.role != "admin":
        raise HTTPException(status_code=403, detail="Only managers can assign courses")

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Toggle
    course.assigned_by_manager = not course.assigned_by_manager
    # In a real app, we would assign to specific users. Here we set the global flag as per schema.
    
    session.add(course)
    session.commit()
    session.refresh(course)
    return course
