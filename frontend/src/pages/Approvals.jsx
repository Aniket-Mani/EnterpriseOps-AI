import { useMemo, useState } from "react";
import { Button, Modal, PageIntro } from "../components/common/UI";
import Status from "../components/common/Status";
import ApprovalSummary from "../components/approvals/ApprovalSummary";
import { downloadCsv } from "../utils/download";

const FILTERS = ["Pending", "Reviewed", "All"];

export default function Approvals({ data }) {
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("Pending");
  const pending = data.approvals.filter((approval) => approval.status === "Pending");
  const visible = useMemo(() => data.approvals.filter((approval) => filter === "All" || (filter === "Pending" ? approval.status === "Pending" : approval.status !== "Pending")), [data.approvals, filter]);

  const decide = async (approval, decision) => {
    try {
      const result = await data.decideApproval(approval, decision, decision === "approved" ? "Reviewed and approved in operations workspace." : "Rejected after review.");
      data.notify(result.source === "api" ? `Approval ${decision} on the operations API` : `Sample approval ${decision}; saved in this browser only`);
      setSelected(null);
    } catch (error) {
      data.notify(`Approval could not be recorded: ${error.message}`);
    }
  };

  const exportQueue = () => downloadCsv([["Approval ID", "Task ID", "Action", "Status", "Requested by", "Source"], ...visible.map((approval) => [approval.id, approval.task, approval.title, approval.status, approval.requestedBy, approval.source])], "enterpriseops-approvals.csv");

  return <>
    <PageIntro eyebrow="GOVERNANCE / HUMAN REVIEW" title="Approval queue" description="Review proposed actions and inspect past decisions." action={<Button variant="secondary" onClick={exportQueue}>↓ Export queue</Button>} />
    <ApprovalSummary count={pending.length}/>
    <div className="toolbar"><div className="tabs">{FILTERS.map((value) => <button key={value} className={filter === value ? "selected" : ""} onClick={() => setFilter(value)}>{value}{value === "Pending" && <span>{pending.length}</span>}</button>)}</div></div>
    <div className="approval-list">{visible.map((approval) => <section className="panel approval-card" key={approval.id}>
      <div className="approval-card-top"><div className="approval-request-icon">↗</div><div className="approval-title"><div><h3>{approval.title}</h3><span className="approval-id">{approval.id} · {approval.task} · {approval.source === "api" ? "LIVE REQUEST" : "SAMPLE REQUEST"}</span></div><Status>{approval.status}</Status></div></div>
      <p>{approval.detail}</p><div className="approval-meta"><span>Requested by <b>{approval.requestedBy}</b></span><span>{approval.time}</span><span className="impact">{approval.impact}</span></div>
      {approval.status === "Pending" && <div className="approval-actions"><button className="button secondary" onClick={() => setSelected(approval)}>Review details</button><button className="button danger-outline" onClick={() => decide(approval, "rejected")}>Reject</button><button className="button primary" onClick={() => decide(approval, "approved")}>✓ Approve action</button></div>}
    </section>)}{visible.length === 0 && <section className="panel empty-state">No {filter.toLowerCase()} approval requests.</section>}</div>
    {selected && <Modal title="Review proposed action" onClose={() => setSelected(null)}><div className="review-detail"><span className="eyebrow">{selected.id} · {selected.task} · {selected.source === "api" ? "LIVE" : "SAMPLE"}</span><h3>{selected.title}</h3><p>{selected.detail}</p>{selected.requestedAction && Object.keys(selected.requestedAction).length > 0 && <><b className="field-label">Requested business change</b><pre className="report-json">{JSON.stringify(selected.requestedAction, null, 2)}</pre></>}<div className="review-facts"><div><small>Requested by</small><b>{selected.requestedBy}</b></div><div><small>Business impact</small><b>{selected.impact}</b></div><div><small>Requested</small><b>{selected.time}</b></div></div><div className="notice">A live approval is sent to the operations API. Sample approval decisions are stored only in this browser.</div></div><footer><Button variant="secondary" onClick={() => setSelected(null)}>Close</Button><Button variant="danger" onClick={() => decide(selected, "rejected")}>Reject action</Button><Button onClick={() => decide(selected, "approved")}>✓ Approve &amp; continue</Button></footer></Modal>}
  </>;
}
