import { Link } from "react-router-dom";

export function TopAppBar() {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1>Sentinel Archive</h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/hub">Model Hub</Link>
          <Link to="/keys">Model Switch</Link>
          <Link to="/settings">Settings</Link>
        </nav>
      </div>
      <div className="topbar-right">LLM Config Manager</div>
    </header>
  );
}
