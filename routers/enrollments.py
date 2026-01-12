from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.deps import get_current_user, require_admin_user, require_employee_user
from db import get_session
from models import CourseEnrollment, Notification, User, EmployeeManager
from schemas import CourseEnrollmentOut, NotificationOut

router = APIRouter(prefix="/api/v1/enrollments", tags=["enrollments"])


@router.get("/me", response_model=list[CourseEnrollmentOut])
def list_my_enrollments(
    session: Session = Depends(get_session),
    employee: User = Depends(require_employee_user),
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


@router.get("/team", response_model=list[CourseEnrollmentOut])
def list_team_enrollments(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user.role != "manager":
         raise HTTPException(status_code=403, detail="Only managers can view team enrollments")

    stmt = (
        select(CourseEnrollment)
        .join(EmployeeManager, CourseEnrollment.employee_id == EmployeeManager.employee_id)
        .where(EmployeeManager.manager_id == user.id)
        .order_by(CourseEnrollment.requested_at.desc())
    )
    return session.exec(stmt).all()


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
