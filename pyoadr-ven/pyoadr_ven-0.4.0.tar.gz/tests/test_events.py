import logging
from datetime import datetime
from datetime import timedelta

import pytest
from freezegun import freeze_time

from .factories import EventFactory
from pyoadr_ven import database
from pyoadr_ven import exceptions
from pyoadr_ven.enums import EventStatus
from pyoadr_ven.enums import OptType
from pyoadr_ven.enums import ReportStatus

_LOGGER = logging.getLogger(__name__)
pytestmark = pytest.mark.pony


class TestSetEventStatusTransition:
    def test_from_unresponded_to_completed(self, mocked_agent):
        event = EventFactory()

        assert event.status == EventStatus.UNRESPONDED.value
        assert mocked_agent.unresponded_events[0] == event
        assert mocked_agent.active_or_pending_events[0] == event
        assert database.Event.get(status=EventStatus.UNRESPONDED.value) == event
        mocked_agent._set_event_status(event.event_id, EventStatus.COMPLETED)
        assert event.status == EventStatus.COMPLETED.value
        assert mocked_agent.active_or_pending_events == []
        assert database.Event.get(status=EventStatus.COMPLETED.value) == event

    def test_from_unresponded_to_near(self, mocked_agent):
        event = EventFactory()
        mocked_agent._set_event_status(event.event_id, EventStatus.NEAR)
        assert event.status == EventStatus.NEAR.value
        assert mocked_agent.active_or_pending_events == [event]
        assert database.Event.get(status=EventStatus.NEAR.value) == event

    def test_from_unresponded_to_far(self, mocked_agent):
        event = EventFactory()
        mocked_agent._set_event_status(event.event_id, EventStatus.FAR)
        assert event.status == EventStatus.FAR.value
        assert mocked_agent.active_or_pending_events == [event]
        assert database.Event.get(status=EventStatus.FAR.value) == event

    def test_from_far_To_active(self, mocked_agent):
        event = EventFactory(
            status=EventStatus.FAR.value, opt_type=OptType.OPT_IN.value
        )
        assert event.status == EventStatus.FAR.value
        mocked_agent._set_event_status(event.event_id, EventStatus.ACTIVE)
        assert mocked_agent.active_or_pending_events == [event]
        assert database.Event.get(status=EventStatus.ACTIVE.value) == event

    def test_opt_in_from_unresponded_to_active(self, mocked_agent):
        event = EventFactory(opt_type=OptType.OPT_IN.value)
        mocked_agent._set_event_status(event.event_id, EventStatus.ACTIVE)
        assert event.status == EventStatus.ACTIVE.value
        assert mocked_agent.active_or_pending_events == [event]
        assert database.Event.get(status=EventStatus.ACTIVE.value) == event

    def test_opt_out_not_transitioned_from_responded_to_active(self, mocked_agent):
        event = EventFactory(opt_type=OptType.OPT_OUT.value)
        with pytest.raises(exceptions.InvalidStatusException):
            mocked_agent._set_event_status(event.event_id, EventStatus.ACTIVE)
            assert event.status != EventStatus.ACTIVE.value
            assert mocked_agent.active_or_pending_events == []

    def test_no_opt_not_transitioned_from_unresponded_to_active(self, mocked_agent):
        event = EventFactory(opt_type=OptType.NONE.value)
        with pytest.raises(exceptions.InvalidStatusException):
            mocked_agent._set_event_status(event.event_id, EventStatus.ACTIVE)
            assert event.status != EventStatus.ACTIVE.value
            assert mocked_agent.active_or_pending_events == []

    def test_from_active_to_completed(self, mocked_agent):
        event = EventFactory(status=EventStatus.ACTIVE.value)
        assert event.status == EventStatus.ACTIVE.value
        mocked_agent._set_event_status(event.event_id, EventStatus.COMPLETED)
        assert event.status == EventStatus.COMPLETED.value
        assert mocked_agent.active_or_pending_events == []
        assert database.Event.get(status=EventStatus.COMPLETED.value) == event

    def test_invalid_status_string(self, mocked_agent):
        event = EventFactory()
        status_before = event.status
        with pytest.raises(exceptions.InvalidStatusException):
            mocked_agent._set_event_status(event.event_id, "invalid thing!")
            assert event.status == status_before

    def test_invalid_status_enum(self, mocked_agent):
        event = EventFactory()
        status_before = event.status
        with pytest.raises(exceptions.InvalidStatusException):
            mocked_agent._set_event_status(event.event_id, ReportStatus.ACTIVE)
            assert event.status == status_before


class TestProcessEvent:
    def test_active_event_opted_in_in_active_events(self, mocked_agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.ACTIVE.value,
            opt_type=OptType.OPT_IN.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event in mocked_agent.active_events
        assert mocked_agent.is_event_in_progress

    def test_active_event_opted_out_not_active_events(self, mocked_agent):
        """ An event shouldn't be able to get into this situation"""
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.ACTIVE.value,
            opt_type=OptType.OPT_OUT.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event not in mocked_agent.active_events

    def test_event_completed_if_over(self, mocked_agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow() - timedelta(minutes=5),
            status=EventStatus.ACTIVE.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.COMPLETED.value
        assert event not in mocked_agent.active_events

    def test_unresponded_event_activated_if_started_and_opted_in(self, mocked_agent):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.OPT_IN.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event in mocked_agent.active_events
        assert mocked_agent.is_event_in_progress is True

    def test_unresponded_event_not_activated_if_started_and_opted_out(
        self, mocked_agent
    ):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.OPT_OUT.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.UNRESPONDED.value
        assert event not in mocked_agent.active_events

    def test_unresponded_event_not_activated_if_started_and_no_opt_type(
        self, mocked_agent
    ):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.UNRESPONDED.value,
            opt_type=OptType.NONE.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.UNRESPONDED.value
        assert event not in mocked_agent.active_events

    def test_active_event_opted_in_immediately_if_active_and_no_opt_type(
        self, mocked_agent
    ):
        event = EventFactory(
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow() + timedelta(hours=1),
            status=EventStatus.ACTIVE.value,
            opt_type=OptType.NONE.value,
        )
        mocked_agent.process_event(event)
        assert event.status == EventStatus.ACTIVE.value
        assert event in mocked_agent.active_events
        assert mocked_agent.is_event_in_progress is True


class TestWithTimeMovingOn:
    def test_event_opted_in_becomes_active(self, mocked_agent):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.OPT_IN.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            frozen_datetime.tick(delta=timedelta(minutes=5))
            mocked_agent.process_event(event)
            assert event.status == EventStatus.ACTIVE.value

    def test_event_far_opted_in_becomes_active(self, mocked_agent):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.FAR.value,
                opt_type=OptType.OPT_IN.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.FAR.value
            frozen_datetime.tick(delta=timedelta(minutes=5))
            mocked_agent.process_event(event)
            assert event.status == EventStatus.ACTIVE.value

    def test_event_opted_out_doesnt_become_active(self, mocked_agent):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.OPT_OUT.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            frozen_datetime.tick(delta=timedelta(minutes=5))
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value


class TestDefaultForceOptIn:
    def test_event_opted_out_doesnt_become_active_before_force_opt_timeout_secs(
        self, mocked_agent
    ):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.OPT_OUT.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            assert event.opt_type == OptType.OPT_OUT.value
            frozen_datetime.tick(
                delta=timedelta(seconds=(mocked_agent.opt_timeout_secs - 5))
            )
            mocked_agent.process_event(event)
            assert event.opt_type == OptType.OPT_OUT.value
            assert event.status == EventStatus.UNRESPONDED.value

    def test_event_opted_out_doesnt_become_opted_in_after_force_opt_timeout_secs(
        self, mocked_agent
    ):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.OPT_OUT.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            assert event.opt_type == OptType.OPT_OUT.value
            frozen_datetime.tick(
                delta=timedelta(seconds=(mocked_agent.opt_timeout_secs + 5))
            )
            mocked_agent.process_event(event)
            assert event.opt_type == OptType.OPT_OUT.value

    def test_event_with_no_opt_type_doesnt_change_opt_type_before_force_opt_timeout_secs(
        self, mocked_agent
    ):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.NONE.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            assert event.opt_type == OptType.NONE.value
            frozen_datetime.tick(
                delta=timedelta(seconds=(mocked_agent.opt_timeout_secs - 5))
            )
            mocked_agent.process_event(event)
            assert event.opt_type == OptType.NONE.value
            assert event.status == EventStatus.UNRESPONDED.value

    def test_event_with_no_opt_type_set_to_default_after_force_opt_timeout_secs(
        self, mocked_agent
    ):
        initial_datetime = datetime(year=2019, month=1, day=1, hour=10, minute=0)
        with freeze_time(initial_datetime) as frozen_datetime:
            event = EventFactory(
                start_time=initial_datetime + timedelta(minutes=5),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created=initial_datetime,
                status=EventStatus.UNRESPONDED.value,
                opt_type=OptType.NONE.value,
            )
            mocked_agent.process_event(event)
            assert event.status == EventStatus.UNRESPONDED.value
            assert event.opt_type == OptType.NONE.value
            frozen_datetime.tick(
                delta=timedelta(seconds=(mocked_agent.opt_timeout_secs + 5))
            )
            mocked_agent.process_event(event)
            assert event.opt_type == mocked_agent.opt_default_decision
