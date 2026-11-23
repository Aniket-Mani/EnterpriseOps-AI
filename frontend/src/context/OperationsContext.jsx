import { createContext, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { approvalsApi, systemApi, tasksApi } from "../services/api";
import { readStorage, writeStorage } from "../utils/storage";
import { seedApprovals, seedTasks } from "../utils/demoData";

export const OperationsContext = createContext(null);

export function OperationsProvider({ children }) {
  const [tasks, setTasks] = useState(() => readStorage("eo.tasks", seedTasks));
  const [approvals, setApprovals] = useState(() => readStorage("eo.approvals", seedApprovals).map((item) => ({ ...item, source: item.source || (String(item.id).startsWith("APR-") ? "demo" : "api") })));
  const [toast, setToast] = useState("");
  const [systemStatus, setSystemStatus] = useState("checking");
  const seenApprovalIds = useRef(null);
  const notify = useCallback((message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 3200);
  }, []);

  useEffect(() => writeStorage("eo.tasks", tasks), [tasks]);
  useEffect(() => writeStorage("eo.approvals", approvals), [approvals]);

  useEffect(() => {
    let mounted = true;
    const refreshApprovals = async () => {
      try {
        const rows = await approvalsApi.list();
        if (!mounted || !Array.isArray(rows)) return;
        const nextIds = new Set(rows.map((approval) => approval.id));
        if (seenApprovalIds.current && [...nextIds].some((id) => !seenApprovalIds.current.has(id)) && readStorage("eo.settings", {}).taskNotifications) {
          notify("A new approval request is waiting");
        }
        seenApprovalIds.current = nextIds;
        const live = rows.map((approval) => ({
        id: approval.id,
        title: approval.description || approval.action_type || "Business action requires approval",
        task: approval.task_id,
        detail: approval.description || "Review the proposed business action and its impact.",
        requestedAction: approval.requested_action || {},
        requestedBy: "EnterpriseOps agent",
        time: approval.requested_at ? new Date(approval.requested_at).toLocaleString() : "Recently",
        impact: approval.action_type || "Business action",
        status: "Pending",
        source: "api",
        }));
        if (live.length) setApprovals((current) => [...live.map((entry) => current.find((item) => item.id === entry.id && item.status !== "Pending") || entry), ...current.filter((item) => !live.some((entry) => entry.id === item.id))]);
      } catch { /* API may be offline; keep browser state available. */ }
    };
    refreshApprovals();
    const timer = window.setInterval(refreshApprovals, 30000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, [notify]);

  useEffect(() => {
    let mounted = true;
    const check = () => systemApi.health().then(() => mounted && setSystemStatus("connected")).catch(() => mounted && setSystemStatus("offline"));
    check();
    const timer = window.setInterval(check, 30000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, []);

  const createTask = useCallback(async (objective, priority = "normal") => {
    const localTask = {
      id: `TASK-${Math.floor(2900 + Math.random() * 99)}`,
      title: objective,
      status: "Running",
      category: "New investigation",
      time: "Just now",
      progress: 8,
      agents: ["Orchestrator", "Order", "Inventory"],
      summary: "Objective received. The orchestrator is assigning investigation steps.",
      priority: priority.replace(/\b\w/g, (letter) => letter.toUpperCase()),
    };
    setTasks((current) => [localTask, ...current]);
    try {
      const result = await tasksApi.create({ objective, priority });
      const task = {
        ...localTask,
        id: result.id || localTask.id,
        task_key: result.task_key || localTask.id,
        title: result.objective || objective,
        status: result.status ? result.status.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()) : localTask.status,
        progress: result.status === "completed" ? 100 : localTask.progress,
        summary: result.final_report?.summary || localTask.summary,
        priority: result.priority || localTask.priority,
        source: "api",
        created_at: result.created_at,
      };
      setTasks((current) => current.map((item) => item.id === localTask.id ? task : item));
      notify("Objective submitted to the operations team");
      return task.id;
    } catch (error) {
      setTasks((current) => current.map((item) => item.id === localTask.id ? { ...item, status: "Local only", source: "local", summary: "The API did not confirm this task. This copy is saved in the browser and its execution status is unknown." } : item));
      notify(`Task submission was not confirmed. Browser copy saved. ${error.message || "Check the API connection."}`);
      return localTask.id;
    }
  }, [notify]);

  const decideApproval = useCallback(async (approval, decision, comment) => {
    if (approval.source === "api") {
      const result = await approvalsApi.decide(approval.id, decision, comment);
      setApprovals((current) => current.map((item) => item.id === approval.id ? { ...item, status: result.status === "approved" ? "Approved" : "Rejected" } : item));
      return { source: "api" };
    }
    setApprovals((current) => current.map((item) => item.id === approval.id ? { ...item, status: decision === "approved" ? "Approved" : "Rejected" } : item));
    return { source: "demo" };
  }, []);

  const retryTask = useCallback(async (task) => {
    try {
      const result = await tasksApi.create({ objective: task.title, priority: (task.priority || "normal").toLowerCase() });
      const updated = {
        ...task,
        id: result.id || task.id,
        task_key: result.task_key || task.task_key || task.id,
        title: result.objective || task.title,
        status: result.status ? result.status.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()) : "Running",
        progress: result.status === "completed" ? 100 : 8,
        source: "api",
        created_at: result.created_at,
        final_report: result.final_report,
      };
      setTasks((current) => current.map((item) => item.id === task.id ? updated : item));
      notify("Task accepted by the operations API");
      return updated.id;
    } catch (error) {
      notify(`Task still was not accepted: ${error.message || "Check the API connection."}`);
      return null;
    }
  }, [notify]);

  const value = useMemo(() => ({ tasks, setTasks, approvals, setApprovals, toast, notify, createTask, retryTask, decideApproval, systemStatus }), [tasks, approvals, toast, notify, createTask, retryTask, decideApproval, systemStatus]);
  return <OperationsContext.Provider value={value}>{children}</OperationsContext.Provider>;
}
