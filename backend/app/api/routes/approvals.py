import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import ApprovalRequest, ApprovalStatus, User
from app.schemas.approval import ApprovalDecision, ApprovalResponse
from app.services.approval_service import (
    review_approval,
    ApprovalNotFoundError,
    UnauthorizedApproverError,
    InvalidApprovalDecisionError,
    ApprovalAlreadyReviewedError,
)


router = APIRouter(
    prefix="/api/approvals",
    tags=["Approvals"],
)

# Development-only identity. Replace with authenticated identity
# resolution before exposing this API outside localhost.
DEV_APPROVER_EMAIL = "approver@enterpriseops.local"


@router.get("", response_model=list[ApprovalResponse])
def list_pending_approvals(
    session: Session = Depends(get_session),
):
    """List pending approval requests."""

    return session.exec(
        select(ApprovalRequest)
        .where(ApprovalRequest.status == ApprovalStatus.PENDING)
        .order_by(ApprovalRequest.requested_at.desc())
    ).all()


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(
    approval_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """Retrieve an approval request."""

    approval = session.get(ApprovalRequest, approval_id)

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )

    return approval


@router.post(
    "/{approval_id}/decision",
    response_model=ApprovalResponse,
)
def decide_approval(
    approval_id: uuid.UUID,
    decision_data: ApprovalDecision,
    session: Session = Depends(get_session),
):
    """Approve or reject a pending request."""

    reviewer = session.exec(
        select(User).where(
            User.email == DEV_APPROVER_EMAIL,
            User.is_active.is_(True),
        )
    ).first()

    if not reviewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development approver account not found or inactive.",
        )

    try:
        return review_approval(
            session=session,
            approval_id=approval_id,
            reviewer_id=reviewer.id,
            decision_data=decision_data,
        )

    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except UnauthorizedApproverError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    except InvalidApprovalDecisionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except ApprovalAlreadyReviewedError as exc:
        raise HTTPException(status_code=409, detail=str(exc))