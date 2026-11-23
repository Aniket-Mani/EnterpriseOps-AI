import { useMemo, useState } from "react";
import { PageIntro, TaskTable } from "../components/common/UI";
import StatCard from "../components/dashboard/StatCard";
import OutcomeDonut from "../components/reports/OutcomeDonut";
import TaskVolumeChart from "../components/reports/TaskVolumeChart";
import { downloadCsv } from "../utils/download";

const FILTERS = ["All task runs", "Completed", "Running", "Needs approval", "Failed", "Local only"];

export default function Reports({ data }) {
  const [filter, setFilter] = useState("All task runs");
  const tasks = data.tasks;
  const filtered = useMemo(() => tasks.filter((task) => filter === "All task runs" || task.status === filter), [tasks, filter]);
  const completed = tasks.filter((task) => task.status === "Completed").length;
  const needsReview = tasks.filter((task) => ["Needs approval", "Waiting for approval"].includes(task.status)).length;
  const failed = tasks.filter((task) => ["Failed", "Local only"].includes(task.status)).length;
  const exportTasks = () => downloadCsv([["Task ID", "Objective", "Status", "Priority", "Category", "Created"], ...filtered.map((task) => [task.task_key || task.id, task.title, task.status, task.priority, task.category, task.created_at || task.time])], "enterpriseops-task-report.csv");

  return <>
    <PageIntro eyebrow="INTELLIGENCE / PERFORMANCE" title="Reports & insights" description="Live summaries calculated from task records saved in this workspace." action={<button className="button secondary" onClick={exportTasks}>↓ Export filtered task report</button>} />
    <div className="report-kpis"><StatCard label="Saved task runs" value={tasks.length} delta="Current history" icon="☷" color="violet"/><StatCard label="Completed" value={completed} delta={`${tasks.length ? Math.round(completed / tasks.length * 100) : 0}% of saved runs`} icon="✓" color="green"/><StatCard label="Needs approval" value={needsReview} delta="Current task states" icon="◷" color="orange"/><StatCard label="Failed / local only" value={failed} delta="Review execution status" icon="!" color="blue"/></div>
    <div className="toolbar report-filter"><div className="tabs">{FILTERS.map((value) => <button key={value} className={filter === value ? "selected" : ""} onClick={() => setFilter(value)}>{value}</button>)}</div></div>
    <div className="report-grid"><TaskVolumeChart tasks={filtered}/><OutcomeDonut tasks={filtered}/></div>
    <section className="panel report-table"><div className="panel-heading"><div><h3>Task records</h3><p>{filtered.length} matching records · summary from the current browser history</p></div><button className="text-button" onClick={exportTasks}>Export CSV ↓</button></div><TaskTable tasks={filtered} compact/></section>
    <div className="info-banner"><span>ⓘ</span><p><b>Report scope.</b> The backend does not provide a task-list or analytics endpoint. These reports reflect the task records stored in this browser and are exported as CSV.</p></div>
  </>;
}
