
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./styles/global.css";

class AppErrorBoundary extends React.Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error) {
    console.error("EnterpriseOps UI failed to render:", error);
  }

  render() {
    if (this.state.error) {
      return <main style={{ maxWidth: 720, margin: "12vh auto", padding: 32, fontFamily: "system-ui, sans-serif", color: "#202633" }}>
        <h1>EnterpriseOps couldn’t load</h1>
        <p>The page hit a frontend error. Refresh to try again; if it repeats, share this message with the developer.</p>
        {import.meta.env.DEV && <pre style={{ whiteSpace: "pre-wrap", background: "#f2f3f6", padding: 16, borderRadius: 8 }}>{this.state.error.message}</pre>}
        <button onClick={() => window.location.reload()} style={{ padding: "10px 14px", border: 0, borderRadius: 6, background: "#6558d9", color: "white" }}>Reload workspace</button>
      </main>;
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppErrorBoundary>
      <BrowserRouter><App /></BrowserRouter>
    </AppErrorBoundary>
  </React.StrictMode>
);
