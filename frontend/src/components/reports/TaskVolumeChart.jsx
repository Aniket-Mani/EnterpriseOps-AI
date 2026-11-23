const groups = [
  { label: "Completed", className: "completed" },
  { label: "Running", className: "running" },
  { label: "Needs approval", className: "approval" },
  { label: "Failed / local", className: "failed" },
];

export default function TaskVolumeChart({ tasks }) {
  const total = tasks.length;
  const countFor = (label) => tasks.filter((task) => {
    if (label === "Completed") return task.status === "Completed";
    if (label === "Running") return task.status === "Running";
    if (label === "Needs approval") return ["Needs approval", "Waiting for approval"].includes(task.status);
    return ["Failed", "Local only"].includes(task.status);
  }).length;
  return <section className="panel chart-panel"><div className="panel-heading"><div><h3>Task status distribution</h3><p>Calculated from saved task history</p></div><span className="chart-total">{total} total</span></div>
    <div className="report-bars">{groups.map((group) => { const count = countFor(group.label); const width = total ? `${Math.max(count / total * 100, count ? 4 : 0)}%` : "0%"; return <div className="report-bar-row" key={group.label}><div><span>{group.label}</span><b>{count}</b></div><div className="report-bar-track"><i className={group.className} style={{ width }} /></div></div>; })}</div>
  </section>;
}
