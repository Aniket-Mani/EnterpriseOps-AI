// In development, Vite proxies API requests to FastAPI to avoid browser CORS errors.
// Production deployments can set VITE_API_URL to the backend origin.
export const API = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const message = await response.text().catch(() => "Request failed");
    throw new Error(message || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export const tasksApi = {
  create: (payload) => request("/api/tasks", { method: "POST", body: JSON.stringify(payload) }),
  get: (taskId) => request(`/api/tasks/${taskId}`),
  report: (taskId) => request(`/api/tasks/${taskId}/report`),
};

export const systemApi = {
  health: () => request("/health"),
};

export const approvalsApi = {
  list: () => request("/api/approvals"),
  get: (approvalId) => request(`/api/approvals/${approvalId}`),
  decide: (approvalId, decision, reviewerComment) => request(`/api/approvals/${approvalId}/decision`, {
    method: "POST",
    body: JSON.stringify({ decision, reviewer_comment: reviewerComment }),
  }),
};
