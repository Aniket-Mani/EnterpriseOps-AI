import { NavLink } from "react-router-dom";
import { Icon } from "../common/UI";
import { getCurrentUser } from "../../services/auth";
import { readStorage } from "../../utils/storage";
import brandMark from "../../assets/enterpriseops-mark.svg";

export default function Sidebar({ tasks, approvals }) {
  const user = getCurrentUser();
  const workspace = readStorage("eo.settings", { workspaceName: "Acme Corporation" });
  const pending = approvals.filter((approval) => approval.status === "Pending").length;
  const active = tasks.filter((task) => task.status === "Running").length;
  return <aside className="sidebar">
    <NavLink className="brand" to="/"><img className="brand-image" src={brandMark} alt=""/><div><b>EnterpriseOps</b><small>INTELLIGENCE PLATFORM</small></div></NavLink>
    <button className="workspace"><span className="workspace-logo">{(workspace.workspaceName || "A").slice(0, 1).toUpperCase()}</span><span><b>{workspace.workspaceName || "Acme Corporation"}</b><small>Operations workspace</small></span><span className="chevron">⌄</span></button>
    <div className="nav-caption">WORKSPACE</div>
    <nav className="nav-list">
      <NavLink end to="/"><Icon>▦</Icon>Overview</NavLink>
      <NavLink to="/tasks"><Icon>☷</Icon>Task runs{active > 0 && <span className="nav-badge">{active}</span>}</NavLink>
      <NavLink to="/approvals"><Icon>◷</Icon>Approvals{pending > 0 && <span className="nav-badge amber">{pending}</span>}</NavLink>
      <div className="nav-caption section-caption">OPERATIONS</div>
      <NavLink to="/orders"><Icon>▤</Icon>Orders</NavLink><NavLink to="/inventory"><Icon>▧</Icon>Inventory</NavLink><NavLink to="/procurement"><Icon>⇄</Icon>Procurement</NavLink>
      <div className="nav-caption section-caption">INTELLIGENCE</div>
      <NavLink to="/agents"><Icon>✧</Icon>Agent team</NavLink><NavLink to="/reports"><Icon>▥</Icon>Reports &amp; insights</NavLink>
    </nav>
    <div className="sidebar-bottom"><NavLink to="/settings"><Icon>⚙</Icon>Settings</NavLink><div className="profile"><div className="avatar">{user.initials}</div><div><b>{user.name}</b><small>{user.role}</small></div><button aria-label="Profile menu">···</button></div></div>
  </aside>;
}
