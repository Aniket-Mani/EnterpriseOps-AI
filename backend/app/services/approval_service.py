import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.models import (
    ApprovalRequest,
    ApprovalStatus,
    AuditLog,
    ActorType,
    User,
)
from app.schemas.approval import ApprovalDecision


# Only these roles may review approval requests.
APPROVER_ROLES = {"admin", "manager", "approver"}


class ApprovalNotFoundError(Exception):
    pass


class UnauthorizedApproverError(Exception):
    pass


class InvalidApprovalDecisionError(Exception):
    pass


class ApprovalAlreadyReviewedError(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc)


def review_approval(
    session: Session,
    approval_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    decision_data: ApprovalDecision,
) -> ApprovalRequest:
    """Review a pending approval and record an audit event."""

    if decision_data.decision not in {
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
    }:
        raise InvalidApprovalDecisionError(
            "Only approved or rejected decisions are permitted."
        )

    # Verify the reviewer is active and has an authorized role.
    reviewer = session.exec(
        select(User)
        .where(
            User.id == reviewer_id,
            User.is_active.is_(True),
        )
        .with_for_update()
    ).first()

    if not reviewer or reviewer.role not in APPROVER_ROLES:
        raise UnauthorizedApproverError(
            "The user is not authorized to review approval requests."
        )

    # Lock the approval row to prevent concurrent reviews.
    approval = session.exec(
        select(ApprovalRequest)
        .where(ApprovalRequest.id == approval_id)
        .with_for_update()
    ).first()

    if not approval:
        raise ApprovalNotFoundError("Approval request not found.")

    if approval.status != ApprovalStatus.PENDING:
        raise ApprovalAlreadyReviewedError(
            f"Approval request is already {approval.status.value}."
        )

    reviewed_at = utc_now()
    previous_status = approval.status

    approval.status = decision_data.decision
    approval.reviewed_at = reviewed_at
    approval.reviewed_by = reviewer.id
    approval.reviewer_comment = decision_data.reviewer_comment

    audit_log = AuditLog(
        task_id=approval.task_id,
        actor_type=ActorType.USER,
        actor_id=reviewer.id,
        action=f"approval_{decision_data.decision.value}",
        entity_type="approval_request",
        entity_id=approval.id,
        description=(
            f"Approval request {approval.id} was "
            f"{decision_data.decision.value} by {reviewer.email}."
        ),
        metadata_json={
            "previous_status": previous_status.value,
            "new_status": decision_data.decision.value,
            "action_type": approval.action_type,
            "reviewer_email": reviewer.email,
            "reviewer_comment": decision_data.reviewer_comment,
            "execution_performed": False,
        },
    )

    session.add(approval)
    session.add(audit_log)

    try:
        # Both the decision and audit record commit together.
        session.commit()
        session.refresh(approval)
        return approval

    except Exception:
        session.rollback()
        raise