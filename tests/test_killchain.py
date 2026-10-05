from ekay.agents import default_agents
from ekay.bus import Event, TriggerBus
from ekay.catalog import CATALOG, phases_count
from ekay.evidence import EvidenceStore
from ekay.findings import FindingStore
from ekay.next_actions import suggest_next
from ekay.phases import KILL_CHAIN, MVP_PHASES, phase_for_family
from ekay.runner import ToolRunner
from ekay.scope import ScopeGuard
from ekay.server import create_app


def test_phases_cover_catalog_families():
    counts = phases_count()
    assert sum(counts.values()) == len(CATALOG)
    assert "recon" in counts
    assert "external" in counts
    assert phase_for_family("ad") == "ad"


def test_catalog_grew_beyond_hexstrike_baseline():
    # HexStrike-class names + EKay red-team extras
    assert len(CATALOG) >= 240
    names = {t.name for t in CATALOG}
    assert "certipy" in names
    assert "linpeas" in names


def test_findings_and_next_actions():
    from ekay.findings import Finding

    store = FindingStore()
    store.add(
        Finding(
            engagement_id="e1",
            kind="port.open",
            title="80",
            data={"host": "127.0.0.1", "port": 80},
            phase="recon",
        )
    )
    g = ScopeGuard(["127.0.0.1"])
    r = ToolRunner(g, allow_intrusive=False)
    out = suggest_next(store, r, "e1", "recon", allow_intrusive=False)
    assert out["finding_count"] == 1
    assert isinstance(out["suggestions"], list)


def test_health_killchain_edition(monkeypatch):
    monkeypatch.delenv("EKAY_TOKEN", raising=False)
    monkeypatch.setenv("EKAY_SCOPE", "127.0.0.1")
    client = create_app().test_client()
    h = client.get("/health").get_json()
    assert h["edition"] == "red-team-kill-chain"
    assert h["version"].startswith("2.")
    assert "recon" in h["phases"]
    assert set(MVP_PHASES).issubset(set(h["mvp_phases"]))


def test_engagement_start_and_findings_api(monkeypatch):
    monkeypatch.delenv("EKAY_TOKEN", raising=False)
    monkeypatch.setenv("EKAY_SCOPE", "127.0.0.1,localhost")
    client = create_app().test_client()
    resp = client.post("/api/engagements", json={"target": "127.0.0.1", "osint": False})
    assert resp.status_code == 200
    data = resp.get_json()
    eid = data["engagement_id"]
    assert data["architecture"] == "kill-chain-trigger-bus"
    findings = client.get("/api/findings", query_string={"engagement_id": eid})
    assert findings.status_code == 200
    nxt = client.get("/api/next", query_string={"engagement_id": eid})
    assert nxt.status_code == 200
    assert "suggestions" in nxt.get_json()


def test_default_agents_register():
    g = ScopeGuard(["127.0.0.1"])
    r = ToolRunner(g)
    ev = EvidenceStore()
    fi = FindingStore()
    agents = default_agents(r, ev, fi)
    names = {a.name for a in agents}
    assert {"recon", "osint", "http_probe", "nuclei", "ad_enum", "report"} <= names
    bus = TriggerBus(max_workers=2)
    for a in agents:
        bus.register(a)
    # report agent on finalize
    bus.publish(Event(kind="engagement.finalize", payload={"target": "127.0.0.1"}, engagement_id="t"))
    bus.wait(timeout=5)
    assert any(j.agent == "report" and j.status == "ok" for j in bus.jobs())
    assert KILL_CHAIN[0] == "osint"
