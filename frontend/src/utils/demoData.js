export const seedTasks = [
  { id: "TASK-2841", title: "Investigate delayed order ORD-1042", status: "Running", category: "Order investigation", time: "2 min ago", progress: 68, agents: ["Order", "Inventory", "Procurement"], summary: "Inventory mismatch identified. Checking alternate warehouse availability.", priority: "High" },
  { id: "TASK-2839", title: "Reconcile low stock for SKU-8821", status: "Needs approval", category: "Inventory allocation", time: "18 min ago", progress: 82, agents: ["Inventory", "Fulfillment", "Verification"], summary: "Transfer of 24 units from Warehouse West is ready for review.", priority: "Medium" },
  { id: "TASK-2837", title: "Review supplier delivery variance", status: "Completed", category: "Supplier investigation", time: "1 hour ago", progress: 100, agents: ["Procurement", "Orchestrator", "Verification"], summary: "Supplier delay confirmed; updated ETA recorded and stakeholders notified.", priority: "Low" },
  { id: "TASK-2834", title: "Resolve fulfillment hold for ORD-1038", status: "Completed", category: "Order fulfillment", time: "3 hours ago", progress: 100, agents: ["Order", "Inventory", "Fulfillment", "Verification"], summary: "Order allocated across two warehouses and independently verified.", priority: "High" },
  { id: "TASK-2828", title: "Prepare replenishment recommendation", status: "Failed", category: "Procurement", time: "Yesterday", progress: 61, agents: ["Procurement", "Inventory"], summary: "Supplier catalog lookup timed out after three attempts.", priority: "Medium" },
];
export const seedApprovals = [
  { id: "APR-1092", title: "Transfer 24 units to Warehouse East", task: "TASK-2839", detail: "Move 24 units of SKU-8821 from Warehouse West to cover two at-risk orders.", requestedBy: "Fulfillment Agent", time: "18 min ago", impact: "Inventory transfer", status: "Pending", source: "demo" },
  { id: "APR-1088", title: "Create purchase order for 120 units", task: "TASK-2821", detail: "Replenish SKU-4402 from Northstar Components. Estimated delivery: 5 business days.", requestedBy: "Procurement Agent", time: "2 hours ago", impact: "$8,640 estimated", status: "Pending", source: "demo" },
];
export const agents = [
  ["✦", "Orchestrator", "Coordinates work across the agent team", "Coordinating", "#7769ed", "12 tasks today"],
  ["▤", "Order Agent", "Investigates orders, customers and shipment status", "Working", "#3889e8", "8 tasks today"],
  ["▦", "Inventory Agent", "Checks stock, reservations and warehouse options", "Working", "#16a67a", "11 tasks today"],
  ["⇄", "Procurement Agent", "Tracks suppliers, purchase orders and replenishment", "Available", "#dd8b34", "5 tasks today"],
  ["↗", "Fulfillment Agent", "Coordinates allocation and order readiness", "Available", "#d66ba0", "7 tasks today"],
  ["✓", "Verification Agent", "Independently validates every business outcome", "Available", "#4d9d9a", "9 tasks today"],
];
export const inventory = [
  ["SKU-8821", "Wireless Headset Pro", "Electronics", 42, 60, "East", "Low stock"], ["SKU-4402", "Industrial Sensor X4", "Components", 186, 120, "Central", "Healthy"], ["SKU-1093", "Packaging Insert · Large", "Packaging", 8, 40, "West", "Critical"], ["SKU-7710", "USB-C Docking Station", "Electronics", 94, 55, "East", "Healthy"], ["SKU-6054", "Thermal Label Roll", "Supplies", 31, 50, "Central", "Low stock"], ["SKU-3208", "Control Module v2", "Components", 0, 24, "West", "Out of stock"],
];
export const orders = [["ORD-1042", "Northwind Trading", "Mar 18, 2025", "12 items", "Delayed", "$4,280"], ["ORD-1041", "Apex Industries", "Mar 18, 2025", "4 items", "Processing", "$1,920"], ["ORD-1040", "Brightline Retail", "Mar 17, 2025", "28 items", "Ready", "$8,640"], ["ORD-1039", "Meridian Supply Co.", "Mar 17, 2025", "7 items", "Shipped", "$2,145"], ["ORD-1038", "Atlas Manufacturing", "Mar 16, 2025", "16 items", "On hold", "$6,320"], ["ORD-1037", "Cobalt Systems", "Mar 16, 2025", "3 items", "Delivered", "$890"]];

export const purchaseOrders = [
  { number: "PO-2084", supplier: "Northstar Components", product: "Industrial Sensor X4", quantity: 120, expected: "Mar 24, 2025", status: "In transit", value: 8640 },
  { number: "PO-2083", supplier: "Pacific Packaging", product: "Packaging Insert · Large", quantity: 500, expected: "Mar 22, 2025", status: "Confirmed", value: 2100 },
  { number: "PO-2081", supplier: "Vertex Electronics", product: "Wireless Headset Pro", quantity: 80, expected: "Mar 20, 2025", status: "Delayed", value: 6400 },
  { number: "PO-2079", supplier: "Northstar Components", product: "Control Module v2", quantity: 60, expected: "Mar 19, 2025", status: "Received", value: 5760 },
];

export const suppliers = [
  { name: "Northstar Components", category: "Electronics", reliability: "96%", leadTime: "5 days", openOrders: 2, status: "Active" },
  { name: "Pacific Packaging", category: "Packaging", reliability: "98%", leadTime: "3 days", openOrders: 1, status: "Active" },
  { name: "Vertex Electronics", category: "Electronics", reliability: "82%", leadTime: "8 days", openOrders: 1, status: "Review" },
  { name: "Meridian Industrial", category: "Components", reliability: "93%", leadTime: "6 days", openOrders: 0, status: "Active" },
];

