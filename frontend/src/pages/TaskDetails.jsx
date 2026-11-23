import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { agents as agentDirectory } from "../utils/demoData";
import { Button } from "../components/common/UI";
import Status from "../components/common/Status";
import TaskProgress from "../components/tasks/TaskProgress";
import { tasksApi } from "../services/api";
import { downloadJson } from "../utils/download";

function statusToProgress(status) {
  if (["Completed", "Cancelled"].includes(status)) return 100;
  if (["Failed", "Local only"].includes(status)) return 0;
  return 8;
}

export default function TaskDetails({ data }) {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const task = useMemo(() => data.tasks.find((item) => item.id === taskId), [data.tasks, taskId]);
  const [refreshing, setRefreshing] = useState(false);
  const isLiveTask = task?.source === "api";

  useEffect(() => {
    if (!isLiveTask) return undefined;
    let mounted = true;
    const refresh = async () => {
      try {
        const current = await tasksApi.get(taskId);
        if (!mounted) return;
        const status = current.status?.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()) || task.status;
        data.setTasks((items) => items.map((item) => item.id === taskId ? {
          ...item,
          title: current.objective || item.title,
          task_key: current.task_key || item.task_key,
          status,
          progress: statusToProgress(status),
          summary: current.final_report?.summary || current.final_report?.root_cause || item.summary,
          final_report: current.final_report,
          updated_at: current.updated_at,
        } : item));
      } catch { /* Keep the last known persisted state visible while offline. */ }
    };
    refresh();
    const timer = window.setInterval(refresh, 8000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, [data.setTasks, isLiveTask, taskId, task?.status]);

  if (!task) return <section className="panel empty-state"><h2>Task not found</h2><p>This task isn’t in this browser’s saved history.</p><Button onClick={() => navigate("/tasks")}>Back to task runs</Button></section>;

  const progress = task.progress ?? statusToProgress(task.status);
  const assignedAgents = task.agents || [];
  const exportReport = async () => {
    try {
      const report = isLiveTask ? await tasksApi.report(task.id) : { objective: task.title, status: task.status, summary: task.summary, note: "Local workspace record; no server execution report is available." };
      downloadJson(report, `${task.task_key || task.id}-report.json`);
      data.notify("Execution report downloaded");
    } catch (error) {
      data.notify(`Report unavailable: ${error.message}`);
    }
  };
  const copySummary = async () => {
    try {
      await navigator.clipboard.writeText(`${task.title}\n${task.summary || "No summary is available yet."}`);
      data.notify("Task summary copied");
    } catch {
      data.notify("Clipboard access is unavailable in this browser");
    }
  };

  return <>
    <button className="back-link" onClick={() => navigate("/tasks")}>← All task runs</button>
    <div className="detail-heading">
      <div>
        <div className="eyebrow">{task.task_key || task.id} <span className="dot-sep">·</span> {task.category || "Operational task"}</div>
        <h2>{task.title}</h2>
        <div className="detail-tags"><Status>{task.status}</Status><span>Started {task.time || (task.created_at ? new Date(task.created_at).toLocaleString() : "time unavailable")}</span><span>Priority: {task.priority || "Normal"}</span></div>
      </div>
      <div className="intro-actions">{task.source === "local" && <Button onClick={async () => { const id = await data.retryTask(task); if (id) navigate(`/tasks/${id}`); }}>↻ Retry API submission</Button>}<Button variant="secondary" onClick={exportReport}>↓ Export report</Button></div>
    </div>
    <div className="detail-grid">
      <div className="main-stack">
        <section className="panel">
          <div className="panel-heading"><div><h3>Execution overview</h3><p>{isLiveTask ? "Status refreshed from the operations API" : "Saved in this browser workspace"}</p></div><span className={`running-live ${refreshing ? "checking" : ""}`}><i />{isLiveTask ? "API SYNC" : "LOCAL RECORD"}</span></div>
          <TaskProgress progress={progress} summary={task.summary || "No execution summary has been returned yet."} />
          <div className="step-list">
            <div className="step"><span className={`step-check ${isLiveTask ? "done" : ""}`}>{isLiveTask ? "✓" : "1"}</span><div><b>Objective recorded</b><small>{isLiveTask ? "Task record exists in the operations API" : "Stored in browser local storage; not submitted to backend"}</small></div><span className="step-time">{task.time || "—"}</span></div>
            <div className="step"><span className={`step-check ${task.final_report ? "done" : ""}`}>{task.final_report ? "✓" : "2"}</span><div><b>Execution result</b><small>{task.final_report ? "Final report available" : "No final report returned yet"}</small></div><span className="step-time">{task.updated_at ? new Date(task.updated_at).toLocaleTimeString() : "—"}</span></div>
            <div className="step"><span className={`step-check ${task.status === "Completed" ? "done" : ""}`}>{task.status === "Completed" ? "✓" : "3"}</span><div><b>Outcome verification</b><small>{task.status === "Completed" ? "Task reports completion" : "Verification detail is not exposed by the current task API"}</small></div><span className="step-time">—</span></div>
          </div>
        </section>
        <section className="panel">
          <div className="panel-heading"><div><h3>Execution report</h3><p>Information available for this task</p></div><button className="text-button" onClick={exportReport}>Download JSON ↓</button></div>
          {task.final_report ? <pre className="report-json">{JSON.stringify(task.final_report, null, 2)}</pre> : <p className="empty-small">The API has not returned a final report for this task.</p>}
          {!task.final_report && isLiveTask && <button className="button secondary" disabled={refreshing} onClick={async () => { setRefreshing(true); try { const report = await tasksApi.report(task.id); data.setTasks((items) => items.map((item) => item.id === task.id ? { ...item, final_report: report } : item)); data.notify("Final report loaded"); } catch (error) { data.notify(`Report not ready: ${error.message}`); } finally { setRefreshing(false); } }}>↻ Check for report</button>}
        </section>
      </div>
      <aside className="right-stack">
        <section className="panel"><div className="panel-heading"><div><h3>Assigned agent team</h3><p>{assignedAgents.length} agents recorded for this task</p></div></div>
          {assignedAgents.length ? assignedAgents.map((name) => { const agent = agentDirectory.find((item) => item[1].startsWith(name)) || agentDirectory[0]; return <div className="assigned-agent" key={name}><span className="agent-mark" style={{ background: `${agent[4]}18`, color: agent[4] }}>{agent[0]}</span><div><b>{agent[1]}</b><small>{isLiveTask ? "Assignment detail from task record" : "Sample workspace assignment"}</small></div><i /></div>; }) : <p className="empty-small">The task API does not expose per-agent assignments.</p>}
        </section>
        <section className="panel report-card"><div className="report-symbol">✧</div><div className="eyebrow">TASK SUMMARY</div><h3>Current findings</h3><p>{task.summary || "No findings have been returned."}</p><button className="full-link" onClick={copySummary}>Copy summary <span>↗</span></button></section>
      </aside>
    </div>
  </>;
}
