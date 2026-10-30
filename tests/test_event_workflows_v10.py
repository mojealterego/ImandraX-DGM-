import asyncio
import pytest
from imandrax_dgm.event_workflows import DurableEventQueue, EventError

def test_event_claim_ack_is_idempotent_and_durable(tmp_path):
    path=tmp_path/"queue.sqlite"
    q=DurableEventQueue(path)
    q.enqueue(event_id="event-1",kind="research.check",payload={"id":"x"},now=100)
    q.enqueue(event_id="event-1",kind="research.check",payload={"id":"x"},now=101)
    with pytest.raises(EventError):
        q.enqueue(event_id="event-1",kind="research.check",payload={"id":"other"},now=102)
    job=q.claim(now=110,lease_seconds=20)
    assert job["event_id"]=="event-1"
    assert DurableEventQueue(path).claim(now=111,lease_seconds=20) is None
    q.ack("event-1",job["lease_token"])
    assert q.claim(now=200,lease_seconds=10) is None
    assert q.status("event-1")["status"]=="DONE"

def test_recovery_and_backoff_and_deadletter(tmp_path):
    q=DurableEventQueue(tmp_path/"q.db")
    q.enqueue(event_id="e",kind="research.check",payload={},now=10)
    first=q.claim(now=10,lease_seconds=5)
    assert q.claim(now=11,lease_seconds=5) is None
    second=q.claim(now=16,lease_seconds=5)
    assert first["lease_token"]!=second["lease_token"]
    with pytest.raises(EventError):
        q.ack("e",first["lease_token"])
    q.fail("e",second["lease_token"],now=17,max_attempts=2)
    assert q.status("e")["status"]=="DEAD"

def test_async_processing_nonexecuting_registered_handler(tmp_path):
    q=DurableEventQueue(tmp_path/"q.db")
    q.enqueue(event_id="e1",kind="research.check",payload={"value":2},now=1)
    async def handler(value):
        return {"result": value["value"]*2}
    count=asyncio.run(q.process_once({"research.check":handler},now=3))
    assert count == 1
    assert q.status("e1")["status"]=="DONE"
    assert q.status("e1")["result"]=={"result":4}
    assert q.verify()

def test_invalid_kind_and_db_corruption_are_rejected(tmp_path):
    q=DurableEventQueue(tmp_path/"q.db")
    with pytest.raises(EventError):
        q.enqueue(event_id="../escape",kind="release.deploy",payload={},now=0)
    q.enqueue(event_id="safe",kind="research.check",payload={},now=0)
    import sqlite3
    with sqlite3.connect(q.path) as con:
        with pytest.raises(sqlite3.DatabaseError):
            con.execute("DELETE FROM task_events")
