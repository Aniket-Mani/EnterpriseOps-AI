import { useLocation } from "react-router-dom";

const titles = { "/": "Overview", "/tasks": "Task runs", "/approvals": "Approvals", "/orders": "Orders", "/inventory": "Inventory", "/procurement": "Procurement", "/agents": "Agent team", "/reports": "Reports & insights", "/settings": "Workspace settings" };

export default function Header({ onNotify, systemStatus, approvalCount }) {
  const location = useLocation();
  const title = location.pathname.startsWith("/tasks/") ? "Task details" : titles[location.pathname] || "EnterpriseOps";
  const currentDate = new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "2-digit", timeZone: "Asia/Kolkata" }).format(new Date()).toUpperCase();
  return <header className="topbar"><div><div className="crumb">Workspace <span>/</span> {title}</div><h1>{title}</h1></div>
    <div className="top-actions"><div className={`connected ${systemStatus}`}><i />{systemStatus === "connected" ? "Operations API connected" : systemStatus === "checking" ? "Checking connection" : "API unavailable · local data"}</div><button className="square-button" aria-label="Notifications" onClick={() => onNotify(approvalCount ? `You have ${approvalCount} approval${approvalCount === 1 ? "" : "s"} waiting for review` : "You're all caught up")}>♧{approvalCount > 0 && <i />}</button><div className="top-divider"/><div className="date-chip">{currentDate}</div></div>
  </header>;
}
