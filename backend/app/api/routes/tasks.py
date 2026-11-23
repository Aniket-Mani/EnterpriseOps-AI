import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import OperationalTask, User
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import create_and_execute_task


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)

DEV_USER_EMAIL = "operator@enterpriseops.local"


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
):
    """Create and execute an operational task."""

    user = session.exec(
        select(User).where(
            User.email == DEV_USER_EMAIL,
            User.is_active.is_(True),
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Development operator account not found.",
        )

    try:
        return create_and_execute_task(
            session=session,
            user_id=user.id,
            task_data=task_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """Retrieve an operational task."""

    task = session.get(OperationalTask, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return task


@router.get("/{task_id}/report")
def get_task_report(
    task_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """Retrieve the final report for an operational task."""

    task = session.get(OperationalTask, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    if task.final_report is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The task does not have a final report yet.",
        )

    return task.final_report