import { format } from "date-fns";
import { LogOut, MessageCircle, Settings, Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useActiveGoal } from "@/hooks/useGoals";
import { useActiveCoaching } from "@/hooks/useCoaching";
import { useAuth } from "@/contexts/AuthContext";
import { ModelSelector } from "./ModelSelector";

function CoachingBadge({ goalId }: { goalId: string }) {
  const { data: session } = useActiveCoaching(goalId);
  if (!session) return null;

  return (
    <Link to={`/goals/${goalId}/coach`}>
      <Badge variant="default" className="gap-1 cursor-pointer">
        <MessageCircle className="w-3 h-3" />
        Priya
      </Badge>
    </Link>
  );
}

export function Header() {
  const today = format(new Date(), "EEEE, MMMM d, yyyy");
  const { data: goal } = useActiveGoal();
  const { user, logout } = useAuth();

  return (
    <header className="border-b px-6 py-3 flex items-center justify-between bg-card">
      <div>
        <h2 className="text-sm text-muted-foreground">{today}</h2>
      </div>
      <div className="flex items-center gap-3">
        {goal && <CoachingBadge goalId={goal.id} />}
        <ModelSelector />
        {user?.is_admin && (
          <Link to="/admin">
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Shield className="w-4 h-4" />
            </Button>
          </Link>
        )}
        <Link to="/settings">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Settings className="w-4 h-4" />
          </Button>
        </Link>
        {user && (
          <div className="flex items-center gap-2">
            {user.picture && (
              <img
                src={user.picture}
                alt={user.name}
                className="w-7 h-7 rounded-full"
                referrerPolicy="no-referrer"
              />
            )}
            <span className="text-sm text-muted-foreground hidden sm:inline">
              {user.name}
            </span>
            <Button variant="ghost" size="icon" onClick={logout} className="h-7 w-7">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
