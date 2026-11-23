export default function ApprovalSummary({ count }) {
  return <div className="approval-summary">
    <div><span className="summary-icon amber">◷</span><div><b>{count} actions require your attention</b><small>Execution pauses until you make a decision.</small></div></div>
    <span className="approval-summary-count">{count} PENDING</span>
  </div>;
}
