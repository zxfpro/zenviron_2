import { Link, useLocation } from "react-router-dom";

const items = [
  { path: "/", label: "Dashboard" },
  { path: "/hub", label: "Model Hub" },
  { path: "/keys", label: "Model Switch" },
  { path: "/settings", label: "Settings" },
];

export function SideNav() {
  const location = useLocation();

  return (
    <aside className="sidenav">
      {items.map((item) => (
        <Link key={item.path} to={item.path} className={location.pathname === item.path ? "active" : ""}>
          {item.label}
        </Link>
      ))}
    </aside>
  );
}
