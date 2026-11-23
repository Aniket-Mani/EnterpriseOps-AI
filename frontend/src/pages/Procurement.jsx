import { useMemo, useState } from "react";
import { Button, Modal, PageIntro } from "../components/common/UI";
import Status from "../components/common/Status";
import { purchaseOrders, suppliers } from "../utils/demoData";

const VIEWS = ["Purchase orders", "Suppliers", "Incoming stock"];

export default function Procurement({ data }) {
  const [tab, setTab] = useState(VIEWS[0]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const [selected, setSelected] = useState(null);
  const records = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (tab === "Suppliers") return suppliers.filter((supplier) => `${supplier.name} ${supplier.category} ${supplier.status}`.toLowerCase().includes(query));
    const candidates = tab === "Incoming stock" ? purchaseOrders.filter((order) => ["In transit", "Confirmed"].includes(order.status)) : purchaseOrders.filter((order) => statusFilter === "All statuses" || order.status === statusFilter);
    return candidates.filter((order) => `${order.number} ${order.supplier} ${order.product} ${order.status}`.toLowerCase().includes(query));
  }, [search, statusFilter, tab]);

  return <>
    <PageIntro eyebrow="PROCUREMENT" title="Procurement" description="Review supplier and inbound stock records, or ask the agent team to investigate." action={<Button onClick={() => data.createTask("Review procurement needs and prepare purchase order recommendations for low stock items.")}>✦ Ask agents to review</Button>} />
    <div className="metric-strip"><div><small>Open purchase orders</small><b>14</b><span>Sample workspace figure</span></div><div><small>Inbound inventory</small><b>1,840</b><span>Sample units in transit</span></div><div><small>Delayed shipments</small><b className="text-orange">2</b><span>Sample supplier records</span></div><div><small>Supplier reliability</small><b>94.2%</b><span>Sample workspace figure</span></div></div>
    <div className="toolbar"><div className="tabs">{VIEWS.map((view) => <button className={tab === view ? "selected" : ""} onClick={() => { setTab(view); setSearch(""); }} key={view}>{view}</button>)}</div><div className="search-box"><span>⌕</span><input aria-label={`Search ${tab.toLowerCase()}`} value={search} onChange={(event) => setSearch(event.target.value)} placeholder={`Search ${tab.toLowerCase()}`} /></div></div>
    {tab === "Purchase orders" && <div className="filter-row">{["All statuses", "In transit", "Confirmed", "Delayed", "Received"].map((status) => <button className={statusFilter === status ? "selected" : ""} onClick={() => setStatusFilter(status)} key={status}>{status}</button>)}</div>}
    <section className="panel table-panel">
      {tab === "Suppliers" ? <table><thead><tr><th>Supplier</th><th>Category</th><th>Reliability</th><th>Lead time</th><th>Open POs</th><th>Status</th><th /></tr></thead><tbody>{records.map((supplier) => <tr key={supplier.name} onClick={() => setSelected(supplier)}><td><b>{supplier.name}</b></td><td>{supplier.category}</td><td>{supplier.reliability}</td><td>{supplier.leadTime}</td><td>{supplier.openOrders}</td><td><Status>{supplier.status}</Status></td><td>↗</td></tr>)}</tbody></table> : <table><thead><tr><th>PO number</th><th>Supplier</th><th>Product</th><th>Quantity</th><th>Expected</th><th>Status</th><th>Value</th><th /></tr></thead><tbody>{records.map((order) => <tr key={order.number} onClick={() => setSelected(order)}><td><b className="link-text">{order.number}</b></td><td>{order.supplier}</td><td>{order.product}</td><td>{order.quantity} units</td><td>{order.expected}</td><td><Status>{order.status}</Status></td><td>${order.value.toLocaleString()}</td><td>↗</td></tr>)}</tbody></table>}
      {records.length === 0 && <div className="empty-state">No {tab.toLowerCase()} match this search.</div>}
    </section>
    <div className="info-banner"><span>ⓘ</span><p><b>Sample procurement records.</b> The current backend does not expose supplier or purchase order endpoints. Search and filters work on this sample set; agent investigations submit through the task API.</p></div>
    {selected && <Modal title={tab === "Suppliers" ? selected.name : selected.number} onClose={() => setSelected(null)}><div className="review-detail">{tab === "Suppliers" ? <><Status>{selected.status}</Status><h3>{selected.category} supplier</h3><p>{selected.reliability} historical reliability · Typical lead time {selected.leadTime} · {selected.openOrders} open purchase orders in this sample.</p></> : <><Status>{selected.status}</Status><h3>{selected.product}</h3><p>{selected.quantity} units from {selected.supplier}, expected {selected.expected}. Sample purchase order value: ${selected.value.toLocaleString()}.</p></>}<div className="notice">This is sample workspace information. No purchase order or supplier record was changed.</div></div><footer><Button variant="secondary" onClick={() => setSelected(null)}>Close</Button><Button onClick={() => { const objective = tab === "Suppliers" ? `Investigate supplier ${selected.name} reliability and delivery risks.` : `Investigate purchase order ${selected.number} from ${selected.supplier}.`; setSelected(null); data.createTask(objective); }}>✦ Investigate with agents</Button></footer></Modal>}
  </>;
}
