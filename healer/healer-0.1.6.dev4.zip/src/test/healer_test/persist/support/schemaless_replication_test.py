import os
import pykka
import logging
import tempfile

from healer.persist.support.schemaless import *
from healer.support.actor.proper import ProperActor, proper_receive_type
from healer.support.typing import override

logger = logging.getLogger(__name__)


class NoSqlTalk:

    @frozen
    class MemberJoin:
        actor_ref:pykka.ActorRef

    @frozen
    class MemberLeave:
        actor_ref:pykka.ActorRef

    @frozen
    class RecordCreate:
        record:str = None
        column:str = None
        bucket:dict = None

    @frozen
    class ReportQuery:
        pass

    @frozen
    class ReportReply:
        content_digest:str
        journal_digest:str

    @frozen
    class CounterQuery:
        pass

    @frozen
    class CounterReply:
        event_count:int = None


class NoSqlStoreActor(NoSqlReplicator, ProperActor):

#     def __init__(self):
#         super().__init__()

    @override
    def on_start(self):
        self.datafile = tempfile.mktemp(prefix="nosql-actor-", suffix=".db")
        self.database = NoSqlDatabase(self.datafile)
        self.store = self.database.store('nosql_store')
        self.store.issue_create()
        self.store.bind_reactor(self)
        self.event_count = 0
        self.member_set:Set[pykka.ActorRef] = set()

    @override
    def on_stop(self):
        self.unbind()
        self.store.issue_delete()
        self.database.close()
        os.remove(self.datafile)

    @proper_receive_type
    def on_member_join(self, message:NoSqlTalk.MemberJoin) -> Any:
        self.member_set.add(message.actor_ref)

    @proper_receive_type
    def on_member_leave(self, message:NoSqlTalk.MemberLeave) -> Any:
        self.member_set.discard(message.actor_ref)

    @proper_receive_type
    def on_record_create(self, message:NoSqlTalk.RecordCreate) -> Any:
        logger.info(message)
        self.store.ensure_record(message.record, **message.bucket)

    @proper_receive_type
    def on_report_query(self, message:NoSqlTalk.ReportQuery) -> Any:
        print(f"event_count={self.event_count}")
        content_digest = self.store.content_digest()
        journal_digest = self.store.journal_digest()
        return NoSqlTalk.ReportReply(content_digest, journal_digest)

    @proper_receive_type
    def on_counter_query(self, message:NoSqlTalk.CounterQuery) -> Any:
        return NoSqlTalk.CounterReply(event_count=self.event_count)

    @proper_receive_type
    def on_remote_event(self, message:NoSqlEvent) -> Any:
        self.event_count += 1
        self.apply_event(message)

    def react_apply_event(self, event:NoSqlEvent) -> None:
        logger.info(f"APPLY: {event} @ {self}")

    def react_local_event(self, event:NoSqlEvent) -> None:
        logger.info(f"LOCAL: {event} @ {self}")
        for member in self.member_set:
            member.tell(event)

    def report_status(self):
        print(f"--- content ---")
        model = self.store.content_model
        for entry in model.select().order_by(model.stamp).tuples():
            print(entry)
        print(f"--- journal ---")
        model = self.store.journal_model
        for entry in model.select().order_by(model.stamp).tuples():
            print(entry)


def test_replication():
    print()

    delay = 0.25
    actor_count = 7
    actor_list = []
    event_count = 3  # number of sent column wirtes

    def mutual_actor_action(action):
        for this in range(actor_count):
            actor_this = actor_list[this]
            for that in range(actor_count):
                actor_that = actor_list[that]
                if actor_this != actor_that:
                    action(actor_this, actor_that)

    action_join = lambda this, that: this.tell(NoSqlTalk.MemberJoin(that))
    action_leave = lambda this, that: this.tell(NoSqlTalk.MemberLeave(that))

    for index in range(actor_count):
        actor_ref = NoSqlStoreActor.start()
        actor_list.append(actor_ref)

    assert len(actor_list) == actor_count

    mutual_actor_action(action_join)

    time.sleep(delay)

    for index in range(actor_count):
        actor_ref = actor_list[index]
        # event_count = 3
        record_one = NoSqlTalk.RecordCreate(
            column="user",
            bucket={
                "name" : f"user-{index}",
                "mail" : f"user-{index}@host",
            }
        )
        actor_ref.tell(record_one)
        record_two = NoSqlTalk.RecordCreate(
            column="info",
            bucket={
                "comment" : f"comment-{index}",
            }
        )
        actor_ref.tell(record_two)

    time.sleep(delay)

    mutual_actor_action(action_leave)

    report_list = list()
    report_set = set()

    for index in range(actor_count):
        actor_ref = actor_list[index]
        report = actor_ref.ask(NoSqlTalk.ReportQuery())
        logger.info(report)
        report_list.append(report)
        report_set.add(report)
        count_test = actor_ref.ask(NoSqlTalk.CounterQuery())
        assert count_test.event_count == (actor_count - 1) * event_count

    assert len(report_list) == actor_count
    assert len(report_set) == 1

    time.sleep(delay)

    for index in range(actor_count):
        actor_ref = actor_list[index]
        actor_ref.stop()
