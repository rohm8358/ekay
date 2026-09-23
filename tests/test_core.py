from ekay.bus import Event, TriggerBus
from ekay.scope import ScopeError, ScopeGuard
from ekay.runner import RunnerError, ToolRunner
from ekay.status import catalog_report


def test_scope_allows_listed_host():
    g = ScopeGuard(["scanme.nmap.org", "127.0.0.1/32"])
    assert g.check("scanme.nmap.org") == "scanme.nmap.org"
    assert g.check("http://127.0.0.1:80/") == "127.0.0.1"


def test_scope_blocks_out_of_scope():
    g = ScopeGuard(["127.0.0.1"])
    try:
        g.check("evil.example")
        raise AssertionError("should have blocked")
    except ScopeError:
        pass


def test_runner_rejects_metacharacters():
    g = ScopeGuard(["127.0.0.1"])
    r = ToolRunner(g, allow_intrusive=False)
    try:
        r.sanitize_args(["-sV", ";reboot"])
        raise AssertionError("should reject")
    except RunnerError:
        pass


def test_intrusive_blocked_without_flag():
    g = ScopeGuard(["127.0.0.1"])
    r = ToolRunner(g, allow_intrusive=False)
    result = r.run("hydra", "127.0.0.1")
    assert result.blocked_reason
    assert "intrusive" in result.blocked_reason


def test_catalog_report_counts_match():
    g = ScopeGuard(["127.0.0.1"])
    r = ToolRunner(g, allow_intrusive=False)
    report = catalog_report(r)
    assert report["catalog"] == report["ready"] + report["missing"] + report["gated"]
    assert report["catalog"] >= 200


class _A:
    name = "alpha"

    def trigger(self, event: Event) -> bool:
        return event.kind == "go"

    def run(self, event: Event) -> dict:
        return {"who": "alpha"}


class _B:
    name = "beta"

    def trigger(self, event: Event) -> bool:
        return event.kind == "go"

    def run(self, event: Event) -> dict:
        return {"who": "beta"}


def test_bus_fires_two_agents_on_same_event():
    bus = TriggerBus(max_workers=4)
    bus.register(_A())
    bus.register(_B())
    fired = bus.publish(Event(kind="go", payload={}, engagement_id="t1"))
    bus.wait(timeout=5)
    assert set(fired) == {"alpha", "beta"}
    names = {j.agent for j in bus.jobs() if j.status == "ok"}
    assert names == {"alpha", "beta"}
