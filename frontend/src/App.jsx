import { Route, Routes } from "react-router-dom";
import Layout from "./components/layout/MainLayout";
import { OperationsProvider } from "./context/OperationsContext";
import Dashboard from "./pages/Dashboard";
import Tasks from "./pages/Tasks";
import TaskDetails from "./pages/TaskDetails";
import Agents from "./pages/Agents";
import Approvals from "./pages/Approvals";
import Orders from "./pages/Orders";
import Inventory from "./pages/Inventory";
import Procurement from "./pages/Procurement";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import { useOperations } from "./hooks/useOperations";

function AppRoutes() {
  const data = useOperations();
  return <Layout data={data}><Routes>
    <Route path="/" element={<Dashboard data={data} />} />
    <Route path="/tasks" element={<Tasks data={data} />} />
    <Route path="/tasks/:taskId" element={<TaskDetails data={data} />} />
    <Route path="/approvals" element={<Approvals data={data} />} />
    <Route path="/orders" element={<Orders data={data} />} />
    <Route path="/inventory" element={<Inventory data={data} />} />
    <Route path="/procurement" element={<Procurement data={data} />} />
    <Route path="/agents" element={<Agents data={data} />} />
    <Route path="/reports" element={<Reports data={data} />} />
    <Route path="/settings" element={<Settings data={data} />} />
    <Route path="*" element={<Dashboard data={data} />} />
  </Routes></Layout>;
}

export default function App() { return <OperationsProvider><AppRoutes /></OperationsProvider>; }
