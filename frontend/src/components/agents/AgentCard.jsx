export default function AgentCard({ agent, index, onInvestigate }) {
  const [icon, name, description, status, color, activity] = agent;
  return <section className="panel agent-card">
    <div className="agent-card-top"><span className="agent-mark large" style={{ background: `${color}18`, color }}>{icon}</span><span className={`agent-state ${status.toLowerCase()}`}><i />{status}</span></div>
    <h3>{name}</h3><p>{description}</p>
    <div className="capabilities"><span>{["Planning", "Delegation", "Shared state"][index % 3]}</span><span>{index === 0 ? "Coordination" : "Business tools"}</span></div>
    <div className="agent-card-foot"><span>{activity}</span><button onClick={onInvestigate}>Create investigation →</button></div>
  </section>;
}
