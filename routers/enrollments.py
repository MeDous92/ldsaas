from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from auth.deps import get_current_user, require_employee_or_manager
from db import get_session
from models import Course, CourseEnrollment, Notification, User, EmployeeManager
from schemas import CourseEnrollmentOut, NotificationOut, TeamEnrollmentOut, CourseOut, UserOut

router = APIRouter(prefix="/api/v1/enrollments", tags=["enrollments"])


class RejectRequest(BaseModel):
    reason: str


@router.get("/me", response_model=list[CourseEnrollmentOut])
def list_my_enrollments(
    session: Session = Depends(get_session),
    employee: User = Depends(require_employee_or_manager),
):
    stmt = select(CourseEnrollment).where(CourseEnrollment.employee_id == employee.id)
    return session.exec(stmt).all()


@router.get("/pending", response_model=list[CourseEnrollmentOut])
def list_pending_enrollments(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role == "admin":
        stmt = select(CourseEnrollment).where(CourseEnrollment.status == "pending")
    elif user.role == "manager":
        # subquery for employees managed by this user
        # We can do a join or subquery. 
        # select CE from CE join EM on CE.emp_id = EM.emp_id where EM.mgr_id = user.id
        stmt = (
            select(CourseEnrollment)
            .join(EmployeeManager, CourseEnrollment.employee_id == EmployeeManager.employee_id)
            .where(
                CourseEnrollment.status == "pending",
                EmployeeManager.manager_id == user.id
            )
        )
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return session.exec(stmt).all()


@router.get("/team", response_model=list[TeamEnrollmentOut])
def list_team_enrollments(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role != "manager" and user.role != "admin":
         raise HTTPException(status_code=403, detail="Only managers can view team enrollments")

    stmt = (
        select(CourseEnrollment, User, Course)
        .join(EmployeeManager, CourseEnrollment.employee_id == EmployeeManager.employee_id)
        .join(User, User.id == CourseEnrollment.employee_id)
        .join(Course, CourseEnrollment.course_id == Course.id)
        .where(EmployeeManager.manager_id == user.id)
        .order_by(CourseEnrollment.requested_at.desc())
    )
    results = session.exec(stmt).all()

    out: list[TeamEnrollmentOut] = []
    for enrollment, employee, course in results:
        out.append(
            TeamEnrollmentOut(
                id=enrollment.id,
                status=enrollment.status,
                deadline=enrollment.deadline,
                requested_at=enrollment.requested_at,
                employee=UserOut.model_validate(employee),
                course=CourseOut.model_validate(course),
            )
        )
    return out


@router.post("/{enrollment_id}/approve", response_model=CourseEnrollmentOut)
def approve_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    approver: User = Depends(get_current_user),
):
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if enrollment.status == "approved":
        return enrollment

    # Permission check
    if approver.role == "admin":
        pass
    elif approver.role == "manager":
        # verify management relationship
        rel = session.exec(
            select(EmployeeManager).where(
                EmployeeManager.manager_id == approver.id,
                EmployeeManager.employee_id == enrollment.employee_id
            )
        ).first()
        if not rel:
            raise HTTPException(status_code=403, detail="Not authorized to approve this employee's request")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    enrollment.status = "approved"
    enrollment.approved_at = datetime.now(timezone.utc)
    enrollment.approved_by = approver.id
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    approver_name = approver.name or approver.email
    try:
        notification = Notification(
            user_id=enrollment.employee_id,
            title="Enrollment approved",
            body=f"Your course enrollment was approved by {approver_name}.",
            type="enrollment_approved",
            meta={
                "enrollment_id": enrollment.id,
                "course_id": enrollment.course_id,
                "approver_id": approver.id,
                "approver_name": approver_name,
            },
        )
        session.add(notification)
        session.commit()
    except Exception as e:
        import traceback
        print(f"FAILED to create notification: {e}")
        traceback.print_exc()

    return enrollment


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(Notification.user_id == user.id).order_by(Notification.id.desc())
    return session.exec(stmt).all()


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.post("/{enrollment_id}/reject", response_model=CourseEnrollmentOut)
def reject_enrollment(
    enrollment_id: int,
    req: RejectRequest,
    session: Session = Depends(get_session),
    rejector: User = Depends(get_current_user),
):
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    if enrollment.status == "rejected":
        return enrollment

    # Permission check
    if rejector.role == "admin":
        pass
    elif rejector.role == "manager":
        # verify management relationship
        rel = session.exec(
            select(EmployeeManager).where(
                EmployeeManager.manager_id == rejector.id,
                EmployeeManager.employee_id == enrollment.employee_id
            )
        ).first()
        if not rel:
            raise HTTPException(status_code=403, detail="Not authorized to reject this employee's request")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    enrollment.status = "rejected"
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)

    rejector_name = rejector.name or rejector.email
    course = session.get(Course, enrollment.course_id)
    course_name = course.name if course else "Unknown Course"

    try:
        notification = Notification(
            user_id=enrollment.employee_id,
            title="Enrollment Rejected",
            body=f"Your request for {course_name} was rejected. Reason: {req.reason}",
            type="enrollment_rejected",
            meta={
                "enrollment_id": enrollment.id,
                "course_id": enrollment.course_id,
                "rejector_id": rejector.id,
                "reason": req.reason,
            },
        )
        session.add(notification)
        session.commit()
    except Exception as e:
        print(f"FAILED to create notification: {e}")

    return enrollment


class AssignmentRequest(BaseModel):
    course_id: int
    employee_id: int
    deadline: Optional[datetime] = None




@router.post("/assign", response_model=CourseEnrollmentOut)
def assign_course_to_employee(
    req: AssignmentRequest,
    session: Session = Depends(get_session),
    manager: User = Depends(get_current_user),
):
    if manager.role != "manager" and manager.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    course = session.get(Course, req.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    employee = session.get(User, req.employee_id)
    if not employee or employee.role != "employee":
        raise HTTPException(status_code=404, detail="Employee not found")

    # 1. Verify manager relationship (skip for admin)
    if manager.role == "manager":
        rel = session.exec(
            select(EmployeeManager).where(
                EmployeeManager.manager_id == manager.id,
                EmployeeManager.employee_id == req.employee_id
            )
        ).first()
        if not rel:
             raise HTTPException(status_code=403, detail="Employee does not report to you")

    # 2. Check if already enrolled
    existing = session.exec(
        select(CourseEnrollment).where(
            CourseEnrollment.employee_id == req.employee_id,
            CourseEnrollment.course_id == req.course_id
        )
    ).first()
    
    if existing:
        # Update deadline if provided
        if req.deadline:
            existing.deadline = req.deadline
            session.add(existing)
            session.commit()
            session.refresh(existing)
        return existing

    # 3. Create Assignment
    enrollment = CourseEnrollment(
        employee_id=req.employee_id,
        course_id=req.course_id,
        status="assigned",  # Distinct status
        deadline=req.deadline,
        approved_at=datetime.now(timezone.utc),  # Auto-approved since assigned by manager
        approved_by=manager.id,
    )
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    
    # Notify Employee
    manager_name = manager.name or manager.email
    try:
        notification = Notification(
            user_id=req.employee_id,
            title="New Mission Assigned",
            body=f"Manager {manager_name} assigned you a new quest.",
            type="quest_assigned",
            meta={
                "course_id": req.course_id,
                "deadline": req.deadline.isoformat() if req.deadline else None,
                "manager_id": manager.id,
                "manager_name": manager_name,
                "enrollment_id": enrollment.id,
            },
        )
        session.add(notification)
        session.commit()
    except Exception as e:
        import traceback
        print(f"FAILED to create notification: {e}")
        traceback.print_exc()
        
    return enrollment
