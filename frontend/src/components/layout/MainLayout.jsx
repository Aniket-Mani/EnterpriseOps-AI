import Sidebar from "./Sidebar";
import Header from "./Header";

export default function MainLayout({ children, data }) {
  return <div className="app-shell"><Sidebar tasks={data.tasks} approvals={data.approvals}/><main className="main"><Header onNotify={data.notify} systemStatus={data.systemStatus} approvalCount={data.approvals.filter((approval) => approval.status === "Pending").length}/><div className="content">{children}</div></main>{data.toast && <div className="toast"><span>✓</span>{data.toast}</div>}</div>;
}
