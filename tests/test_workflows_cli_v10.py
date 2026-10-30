"""CLI covers the same installed ImandraX package (not a separate engine)."""
import json
from pathlib import Path
from imandrax_dgm.cli import main

ROOT=Path(__file__).resolve().parents[1]

def run(argv, capsys, file, data):
    file.write_text(json.dumps(data),encoding="utf-8")
    assert main(argv)==0
    return json.loads(capsys.readouterr().out)

def test_full_media_audit_cli(capsys):
    assert main(["--root",str(ROOT),"media-audit","--limit","10"])==0
    result=json.loads(capsys.readouterr().out)
    assert result["inventory_total"]==701
    assert result["integrated_count"]==0
    assert result["root_readme_inspected"]==12
    assert len(result["items"])==10

def test_tree_rewoo_and_event_cli(tmp_path,capsys):
    f=tmp_path/"data.json"; state=tmp_path/"state"
    args=["--root",str(ROOT),"cognitive","--state-dir",str(state),
          "--op","tot","--payload-file",str(f)]
    out=run(args,capsys,f,{"beam_width":1,"max_depth":2,
                           "thoughts":[{"node_id":"root","parent":None,
                                        "depth":0,"score":.7,"sources":[]}]})
    assert out["status"]=="HEURISTIC_PATH_NOT_PROOF"
    args[args.index("tot")]="rewoo-validate"
    out=run(args,capsys,f,{"tools":[{"name":"lookup","ontology":"knowledge.retrieve",
                                     "input_fields":["id"],"access":"READ"}],
                           "steps":[{"step_id":"s1","tool":"lookup",
                                     "params":{"id":"x"},"depends_on":[]}]})
    assert out["waves"]==[["s1"]]
    args[args.index("rewoo-validate")]="event-enqueue"
    out=run(args,capsys,f,{"event_id":"check1","kind":"research.check",
                           "payload":{"tenant":"lab","hypothesis_id":"h1",
                                      "required_fact_ids":["missing"],
                                      "valid_at":"2026-10-30T00:00:00Z"},"now":1})
    assert out["status"]=="ENQUEUED"
    args[args.index("event-enqueue")]="event-process"
    out=run(args,capsys,f,{"now":2})
    assert out["processed"]==1
    args[args.index("event-process")]="event-status"
    out=run(args,capsys,f,{"event_id":"check1"})
    assert out["status"]=="DONE"
    assert out["result"]["status"]=="UNSUPPORTED_MISSING_REFERENCES"
