import { Link, useLocation } from "react-router-dom";
import { Home, Target, TrendingUp, Plus, CheckSquare, Activity } from "lucide-react";
import { useActiveGoal } from "@/hooks/useGoals";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export function Sidebar() {
  const location = useLocation();
  const { data: goal } = useActiveGoal();

  const navItems = [
    { to: "/", icon: Home, label: "Today" },
    { to: "/habits", icon: CheckSquare, label: "Habits" },
    { to: "/trackers", icon: Activity, label: "Trackers" },
    { to: "/progress", icon: TrendingUp, label: "Progress" },
  ];

  return (
    <aside className="w-64 border-r bg-card h-screen flex flex-col">
      <div className="p-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">K</span>
          </div>
          <span className="font-semibold text-lg">Kairos</span>
        </Link>
      </div>

      <Separator />

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
              location.pathname === item.to
                ? "bg-accent text-accent-foreground font-medium"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            }`}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </Link>
        ))}

        <Separator className="my-3" />

        <div className="flex items-center justify-between px-3 mb-2">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Goal
          </span>
          {!goal && (
            <Link to="/goals/new">
              <Button variant="ghost" size="icon" className="h-5 w-5">
                <Plus className="w-3 h-3" />
              </Button>
            </Link>
          )}
        </div>

        {goal ? (
          <Link
            to={`/goals/${goal.id}`}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
              location.pathname === `/goals/${goal.id}`
                ? "bg-accent text-accent-foreground font-medium"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            }`}
          >
            <Target className="w-4 h-4 shrink-0" />
            <span className="truncate">{goal.title}</span>
          </Link>
        ) : (
          <p className="px-3 text-xs text-muted-foreground">
            No active goal
          </p>
        )}
      </nav>
    </aside>
  );
}
