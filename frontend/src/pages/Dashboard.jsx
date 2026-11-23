import { useNavigate } from "react-router-dom";
import { agents, inventory, orders } from "../utils/demoData";
import { TaskComposer, TaskTable } from "../components/common/UI";
import Status from "../components/common/Status";
import StatCard from "../components/dashboard/StatCard";

export default function Dashboard({ data }) {
  const navigate = useNavigate();
  const running = data.tasks.filter((task) => task.status === "Running");
  const pendingApprovals = data.approvals.filter((approval) => approval.status === "Pending");
  const completed = data.tasks.filter((task) => task.status === "Completed").length;
  const completionRate = data.tasks.length ? `${Math.round((completed / data.tasks.length) * 100)}%` : "—";
  const lowStock = inventory.filter((item) => ["Low stock", "Critical", "Out of stock"].includes(item[6])).length;

  return <>
    <div className="welcome-row"><div><div className="eyebrow">OPERATIONS WORKSPACE</div><h2>Good morning, Aniket <span className="wave">✦</span></h2><p>Review current task activity and operational records.</p></div><TaskComposer onSubmit={async (objective, priority) => { const id = await data.createTask(objective, priority); navigate(`/tasks/${id}`); }} /></div>
    <div className="stats-grid">
      <StatCard label="Running tasks" value={running.length} delta={`${pendingApprovals.length} approvals`} icon="◷" color="violet" />
      <StatCard label="Orders in sample view" value={orders.length} delta="Sample records" icon="▤" color="blue" />
      <StatCard label="Low stock items" value={lowStock} delta="Sample records" icon="▧" color="orange" />
      <StatCard label="Completed tasks" value={completionRate} delta={`${completed} of ${data.tasks.length} saved`} icon="✓" color="green" />
    </div>
    <div className="dashboard-grid">
      <section className="panel activity-panel">
        <div className="panel-heading"><div><h3>Current task activity</h3><p>Saved task status from this workspace</p></div><button className="text-button" onClick={() => navigate("/tasks")}>View task history →</button></div>
        {running[0] ? <div className="live-task"><div className="live-indicator"><i /></div><div className="live-main"><div className="live-title"><b>{running[0].title}</b><Status>{running[0].status}</Status></div><p>{running[0].summary}</p><div className="progress-track"><span style={{ width: `${running[0].progress || 0}%` }} /></div><div className="progress-meta"><span>{running[0].source === "api" ? "Status from operations API" : "Browser-saved task record"}</span><span>{running[0].progress || 0}%</span></div><div className="agent-avatars">{(running[0].agents || []).map((agent, index) => <span key={agent} className={`mini-avatar ${["blue", "green", "orange"][index % 3]}`} title={agent}>{agent[0]}</span>)}<small>{(running[0].agents || []).join(" · ") || "No agent assignments available"}</small><button className="inline-link" onClick={() => navigate(`/tasks/${running[0].id}`)}>Open task →</button></div></div></div> : <div className="empty-small">No tasks are currently marked as running.</div>}
        <div className="activity-divider"/><div className="panel-subhead"><b>Recent task runs</b><button className="text-button" onClick={() => navigate("/tasks")}>See all →</button></div><TaskTable tasks={data.tasks.slice(0, 4)} compact onOpen={(id) => navigate(`/tasks/${id}`)} />
      </section>
      <aside className="right-stack">
        <section className="panel approval-widget"><div className="panel-heading"><div><h3>Needs your review</h3><p>{pendingApprovals.length} pending actions</p></div><span className="approval-count">{pendingApprovals.length}</span></div>{pendingApprovals.slice(0, 2).map((approval) => <div className="approval-mini" key={approval.id}><div className="approval-icon">↗</div><div><b>{approval.title}</b><small>{approval.requestedBy} · {approval.time}</small></div><button onClick={() => navigate("/approvals")}>Review</button></div>)}{pendingApprovals.length === 0 && <div className="empty-small">No actions need review.</div>}<button className="full-link" onClick={() => navigate("/approvals")}>Open approval queue <span>→</span></button></section>
        <section className="panel health-panel"><div className="panel-heading"><div><h3>Agent roster</h3><p>{agents.length} configured sample agents</p></div><button className="text-button" onClick={() => navigate("/agents")}>View team</button></div><div className="agent-health-list">{agents.slice(0, 4).map((agent) => <div className="agent-health" key={agent[1]}><span className="agent-mark" style={{ background: `${agent[4]}18`, color: agent[4] }}>{agent[0]}</span><b>{agent[1]}</b><span className={`agent-state ${agent[3].toLowerCase()}`}><i />{agent[3]}</span></div>)}</div><small className="sample-caption">The backend does not currently provide agent status.</small></section>
      </aside>
    </div>
  </>;
}
