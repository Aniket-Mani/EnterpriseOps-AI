import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageIntro, TaskComposer, TaskTable } from "../components/common/UI";
import { downloadCsv } from "../utils/download";

export default function Tasks({ data }) {
  const [filter, setFilter] = useState("All tasks");
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const filters = ["All tasks", ...new Set(data.tasks.map((task) => task.status))];
  const list = useMemo(() => data.tasks.filter((task) => (filter === "All tasks" || task.status === filter) && `${task.title} ${task.id} ${task.task_key || ""}`.toLowerCase().includes(search.toLowerCase())), [data.tasks, filter, search]);
  const exportList = () => downloadCsv([["Task ID", "Objective", "Status", "Category", "Priority", "Created"], ...list.map((task) => [task.task_key || task.id, task.title, task.status, task.category, task.priority, task.created_at || task.time])], "enterpriseops-task-history.csv");

  return <>
    <PageIntro eyebrow="WORKSPACE / EXECUTION" title="Task runs" description="Search saved tasks, inspect execution records, or submit a new objective." action={<div className="intro-actions"><button className="button secondary" onClick={exportList}>↓ Export filtered</button><TaskComposer compact onSubmit={async (objective, priority) => { const id = await data.createTask(objective, priority); navigate(`/tasks/${id}`); }} /></div>} />
    <div className="toolbar"><div className="tabs">{filters.map((value) => <button key={value} className={filter === value ? "selected" : ""} onClick={() => setFilter(value)}>{value}{value === "All tasks" && <span>{data.tasks.length}</span>}</button>)}</div><div className="search-box"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search task or ID" /></div></div>
    <section className="panel table-panel"><TaskTable tasks={list} onOpen={(id) => navigate(`/tasks/${id}`)} />{list.length === 0 && <div className="empty-state">No tasks match this filter.</div>}<div className="table-footer">Showing <b>{list.length}</b> saved task runs <span>Stored in this browser</span></div></section>
    <div className="info-banner"><span>ⓘ</span><p><b>History scope.</b> The backend supports task creation and lookup by ID, but has no list endpoint. This page combines browser-saved records with tasks created from this workspace.</p></div>
  </>;
}
