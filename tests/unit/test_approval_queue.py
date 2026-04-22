"""Unit tests for ApprovalQueue — ANIF-404 §4.4."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from anif_platform.human_loop.models import ApprovalTicketRow, TicketStatus
from anif_platform.human_loop.queue import ApprovalQueue, TicketError


def make_ticket(
    status: str = "pending",
    requested_by: str = "jsmith@example.com",
    expires_at: datetime | None = None,
) -> ApprovalTicketRow:
    now = datetime.now(UTC)
    t = ApprovalTicketRow()
    t.ticket_id = str(uuid.uuid4())
    t.intent_id = uuid.uuid4()
    t.status = status
    t.requested_by = requested_by
    t.decision_summary = "Test action requires approval"
    t.risk_score = 74
    t.required_approver_role = "senior_engineer"
    t.created_at = now
    t.expires_at = expires_at or (now + timedelta(minutes=15))
    return t


def make_queue() -> tuple[ApprovalQueue, AsyncMock, AsyncMock]:
    session = AsyncMock()
    writer = AsyncMock()
    queue = ApprovalQueue(session=session, writer=writer)
    return queue, session, writer


class TestCreateTicket:
    @pytest.mark.asyncio
    async def test_ticket_created_with_pending_status(self) -> None:
        """ANIF-404 §4.4.1: initial status MUST be pending."""
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        ticket = await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=74,
            decision_summary="High-risk reroute_traffic on prod segment",
        )
        assert ticket.status == TicketStatus.pending

    @pytest.mark.asyncio
    async def test_ticket_expires_at_is_15_minutes_after_created(self) -> None:
        """ANIF-404 §4.4.1: expires_at MUST be exactly 15 minutes after created_at."""
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        ticket = await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=50,
            decision_summary="apply_qos in prod",
        )
        delta = ticket.expires_at - ticket.created_at
        assert delta == timedelta(minutes=15)

    @pytest.mark.asyncio
    async def test_create_writes_audit_before_returning(self) -> None:
        """ANIF-404 §4.4.1: audit record MUST be written before returning."""
        queue, session, writer = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        await queue.create_ticket(
            intent_id=uuid.uuid4(),
            operator_id="jsmith@example.com",
            risk_score=50,
            decision_summary="apply_qos in prod",
        )
        writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_ticket_id_is_unique_uuid(self) -> None:
        queue, session, _ = make_queue()
        session.add = MagicMock()
        session.flush = AsyncMock()
        t1 = await queue.create_ticket(uuid.uuid4(), "a@example.com", 50, "action A")
        t2 = await queue.create_ticket(uuid.uuid4(), "b@example.com", 50, "action B")
        assert t1.ticket_id != t2.ticket_id
        uuid.UUID(t1.ticket_id)  # must be valid UUID; raises if not


class TestApproveTicket:
    @pytest.mark.asyncio
    async def test_approve_requires_senior_engineer_role(self) -> None:
        """ANIF-404 §4.4.4: approver MUST have senior_engineer role."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="senior_engineer"):
            await queue.approve(
                ticket_id=ticket.ticket_id,
                approver_id="bjones@example.com",
                approver_roles=["network_engineer"],
                notes=None,
            )

    @pytest.mark.asyncio
    async def test_self_approval_refused(self) -> None:
        """ANIF-404 §4.4.4: approver MUST be different from submitter."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="self-approval"):
            await queue.approve(
                ticket_id=ticket.ticket_id,
                approver_id="jsmith@example.com",
                approver_roles=["senior_engineer"],
                notes=None,
            )

    @pytest.mark.asyncio
    async def test_approve_non_pending_ticket_raises(self) -> None:
        """ANIF-404 §4.4.4: approval of expired/rejected/approved ticket MUST be refused."""
        queue, session, _ = make_queue()
        for terminal_status in ("approved", "rejected", "expired"):
            ticket = make_ticket(status=terminal_status)
            session.get = AsyncMock(return_value=ticket)
            with pytest.raises(TicketError, match="not in pending"):
                await queue.approve(
                    ticket_id=ticket.ticket_id,
                    approver_id="bjones@example.com",
                    approver_roles=["senior_engineer"],
                    notes=None,
                )

    @pytest.mark.asyncio
    async def test_approve_writes_audit_before_returning(self) -> None:
        """ANIF-404 §4.4.4: audit MUST be written before success response."""
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        await queue.approve(
            ticket_id=ticket.ticket_id,
            approver_id="bjones@example.com",
            approver_roles=["senior_engineer"],
            notes="Looks safe",
        )
        writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_sets_status_to_approved(self) -> None:
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending", requested_by="jsmith@example.com")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        result = await queue.approve(
            ticket_id=ticket.ticket_id,
            approver_id="bjones@example.com",
            approver_roles=["senior_engineer"],
            notes=None,
        )
        assert result.status == TicketStatus.approved
        assert result.approved_by == "bjones@example.com"


class TestRejectTicket:
    @pytest.mark.asyncio
    async def test_reject_without_reason_raises(self) -> None:
        """ANIF-404 §4.4.5: reason MUST be provided."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="reason"):
            await queue.reject(
                ticket_id=ticket.ticket_id,
                operator_id="bjones@example.com",
                operator_roles=["network_engineer"],
                reason="",
            )

    @pytest.mark.asyncio
    async def test_reject_requires_network_engineer_role(self) -> None:
        """ANIF-404 §4.4.5: rejector MUST have network_engineer role."""
        queue, session, _ = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)

        with pytest.raises(TicketError, match="role"):
            await queue.reject(
                ticket_id=ticket.ticket_id,
                operator_id="bjones@example.com",
                operator_roles=["read_only"],
                reason="Too risky",
            )

    @pytest.mark.asyncio
    async def test_reject_sets_status_to_rejected(self) -> None:
        queue, session, writer = make_queue()
        ticket = make_ticket(status="pending")
        session.get = AsyncMock(return_value=ticket)
        session.flush = AsyncMock()

        result = await queue.reject(
            ticket_id=ticket.ticket_id,
            operator_id="bjones@example.com",
            operator_roles=["network_engineer"],
            reason="Policy violation observed",
        )
        assert result.status == TicketStatus.rejected
        assert result.rejection_reason == "Policy violation observed"


class TestExpirePending:
    @pytest.mark.asyncio
    async def test_overdue_pending_ticket_is_expired(self) -> None:
        """ANIF-406 §4.4.3: ticket past expires_at MUST transition to expired."""
        queue, session, writer = make_queue()
        overdue = make_ticket(
            status="pending",
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [overdue]
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        expired_ids = await queue.expire_pending()
        assert overdue.ticket_id in expired_ids
        assert overdue.status == TicketStatus.expired

    @pytest.mark.asyncio
    async def test_expire_writes_audit_for_each_expired_ticket(self) -> None:
        """ANIF-406 §4.4.3: audit record MUST be written for each expiry event."""
        queue, session, writer = make_queue()
        overdue1 = make_ticket(status="pending", expires_at=datetime.now(UTC) - timedelta(seconds=1))
        overdue2 = make_ticket(status="pending", expires_at=datetime.now(UTC) - timedelta(seconds=1))

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [overdue1, overdue2]
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        await queue.expire_pending()
        assert writer.write.call_count == 2

    @pytest.mark.asyncio
    async def test_non_overdue_pending_ticket_not_expired(self) -> None:
        queue, session, writer = make_queue()
        fresh = make_ticket(
            status="pending",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=mock_result)
        session.flush = AsyncMock()

        expired_ids = await queue.expire_pending()
        assert fresh.ticket_id not in expired_ids
        assert fresh.status == TicketStatus.pending
