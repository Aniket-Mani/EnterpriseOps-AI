export default function TaskProgress({ progress, summary }) {
  return <div className="task-progress">
    <div><strong>{progress}%</strong><span>completion</span></div>
    <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
    <small>{summary}</small>
  </div>;
}
