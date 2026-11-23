import { useState } from "react";
import { Button, PageIntro } from "../components/common/UI";
import { API, systemApi } from "../services/api";
import { getCurrentUser, saveCurrentUser } from "../services/auth";
import { readStorage, writeStorage } from "../utils/storage";

const DEFAULTS = {
  workspaceName: "Acme Corporation",
  timezone: "Asia/Kolkata",
  currency: "USD",
  purchaseOrderApproval: true,
  inventoryTransferApproval: true,
  requireVerification: true,
  taskNotifications: false,
  maxConcurrentTasks: 5,
  maxRetries: 3,
};
const SECTIONS = ["Workspace", "Approvals & safety", "Agent policies", "Notifications", "Connections"];

export default function Settings({ data }) {
  const [tab, setTab] = useState("Workspace");
  const [settings, setSettings] = useState(() => ({ ...DEFAULTS, ...readStorage("eo.settings", {}) }));
  const [profile, setProfile] = useState(() => getCurrentUser());
  const [connection, setConnection] = useState(data.systemStatus);
  const [saved, setSaved] = useState(true);
  const update = (key, value) => { setSettings((current) => ({ ...current, [key]: value })); setSaved(false); };

  const save = () => {
    writeStorage("eo.settings", settings);
    saveCurrentUser(profile);
    setSaved(true);
    data.notify("Workspace preferences saved in this browser");
  };

  const checkConnection = async () => {
    setConnection("checking");
    try { await systemApi.health(); setConnection("connected"); data.notify("Operations API is reachable"); }
    catch { setConnection("offline"); data.notify("Operations API could not be reached"); }
  };

  const toggle = (key, label, description) => <label className="setting-option" key={key}>
    <span><b>{label}</b><small>{description}</small></span>
    <input type="checkbox" checked={settings[key]} onChange={(event) => update(key, event.target.checked)} /><i />
  </label>;

  return <>
    <PageIntro eyebrow="ADMINISTRATION" title="Workspace settings" description="Manage workspace preferences and local review policies." />
    <div className="settings-layout">
      <nav className="settings-nav" aria-label="Settings sections">{SECTIONS.map((section) => <button className={tab === section ? "selected" : ""} key={section} onClick={() => setTab(section)}>{section}</button>)}</nav>
      <section className="panel settings-panel">
        <div className="settings-title"><h3>{tab}</h3><p>{tab === "Workspace" ? "Organization profile and regional preferences." : `Configure ${tab.toLowerCase()} for this browser workspace.`}</p></div>
        {tab === "Workspace" && <>
          <label className="field-label" htmlFor="workspace-name">Workspace name</label><input id="workspace-name" className="form-input" value={settings.workspaceName} onChange={(event) => update("workspaceName", event.target.value)} />
          <label className="field-label" htmlFor="workspace-timezone">Default timezone</label><select id="workspace-timezone" className="form-input" value={settings.timezone} onChange={(event) => update("timezone", event.target.value)}><option value="Asia/Kolkata">Asia/Kolkata (IST)</option><option value="UTC">UTC</option><option value="America/Los_Angeles">America/Los_Angeles (PST)</option><option value="Europe/London">Europe/London (GMT)</option></select>
          <label className="field-label" htmlFor="workspace-currency">Default currency</label><select id="workspace-currency" className="form-input" value={settings.currency} onChange={(event) => update("currency", event.target.value)}><option value="USD">USD — US Dollar</option><option value="INR">INR — Indian Rupee</option><option value="EUR">EUR — Euro</option><option value="GBP">GBP — Pound Sterling</option></select>
          <label className="field-label" htmlFor="profile-name">Your display name</label><input id="profile-name" className="form-input" value={profile.name} onChange={(event) => { setProfile((current) => ({ ...current, name: event.target.value, initials: event.target.value.split(/\s+/).filter(Boolean).map((word) => word[0]).join("").slice(0, 2).toUpperCase() })); setSaved(false); }} />
        </>}
        {tab === "Approvals & safety" && <div className="settings-options">
          {toggle("purchaseOrderApproval", "Require review for purchase orders", "Keep proposed purchase orders paused until an operator approves them.")}
          {toggle("inventoryTransferApproval", "Require review for inventory transfers", "Review transfers between warehouses before execution.")}
          {toggle("requireVerification", "Require independent verification", "Prefer a verification step after business actions.")}
        </div>}
        {tab === "Agent policies" && <>
          <label className="field-label" htmlFor="concurrent-tasks">Preferred concurrent task limit</label><select id="concurrent-tasks" className="form-input" value={settings.maxConcurrentTasks} onChange={(event) => update("maxConcurrentTasks", Number(event.target.value))}>{[1, 2, 3, 5, 8, 10].map((value) => <option key={value} value={value}>{value} tasks</option>)}</select>
          <label className="field-label" htmlFor="retry-limit">Preferred retry limit</label><select id="retry-limit" className="form-input" value={settings.maxRetries} onChange={(event) => update("maxRetries", Number(event.target.value))}>{[0, 1, 2, 3, 5].map((value) => <option key={value} value={value}>{value} retries</option>)}</select>
          <p className="settings-note">These are saved as workspace preferences. The current API does not expose policy configuration, so they do not change backend execution.</p>
        </>}
        {tab === "Notifications" && <div className="settings-options">{toggle("taskNotifications", "Notify me when a task needs review", "Show an in-app notification when an approval arrives.")}</div>}
        {tab === "Connections" && <div className="connection-card"><div className={`connection-indicator ${connection}`}><i />{connection === "connected" ? "Connected" : connection === "checking" ? "Checking" : "Unavailable"}</div><p>Operations API</p><code>{API || "Same origin · Vite development proxy"}</code><small>Task creation and approval decisions use this API. Order, inventory, procurement, agent registry, authentication and WebSocket endpoints are not currently exposed.</small><Button variant="secondary" onClick={checkConnection} disabled={connection === "checking"}>↻ Test connection</Button></div>}
        <div className="settings-footer"><span>{saved ? "All changes saved on this browser" : "Unsaved changes"}</span><Button onClick={save} disabled={saved}>Save changes</Button></div>
      </section>
    </div>
  </>;
}
