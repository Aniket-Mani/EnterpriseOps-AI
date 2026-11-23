export default function OutcomeDonut({ tasks }) {
  const total = tasks.length;
  const completed = tasks.filter((task) => task.status === "Completed").length;
  const review = tasks.filter((task) => ["Needs approval", "Waiting for approval"].includes(task.status)).length;
  const failed = tasks.filter((task) => ["Failed", "Local only"].includes(task.status)).length;
  const active = Math.max(total - completed - review - failed, 0);
  const pct = (value) => total ? `${(value / total) * 100}%` : "0%";
  const first = pct(completed);
  const second = `${(total ? (completed + review) / total * 100 : 0)}%`;
  const third = `${(total ? (completed + review + failed) / total * 100 : 0)}%`;
  return <section className="panel outcomes-panel"><div className="panel-heading"><div><h3>Task outcomes</h3><p>Across {total} saved task runs</p></div></div>
    <div className="donut-wrap"><div className="donut" style={{ background: `conic-gradient(#20a478 0 ${first}, #eeb14c ${first} ${second}, #dc6d72 ${second} ${third}, #dce0e8 ${third} 100%)` }}><div><b>{total}</b><small>Total runs</small></div></div>
      <div className="donut-legend"><span><i className="green-dot" />Completed <b>{completed}</b></span><span><i className="orange-dot" />Needs review <b>{review}</b></span><span><i className="red-dot" />Failed / local <b>{failed}</b></span><span><i className="neutral-dot" />Other status <b>{active}</b></span></div>
    </div>
  </section>;
}
