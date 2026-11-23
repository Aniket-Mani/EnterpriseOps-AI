export default function Status({ children }) { return <span className={`status-pill ${String(children).toLowerCase().replaceAll(" ", "-")}`}><i />{children}</span>; }
