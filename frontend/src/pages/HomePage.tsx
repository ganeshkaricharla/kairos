import { Link } from "react-router-dom";
import { Plus, Target } from "lucide-react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { DailyChecklist } from "@/components/daily/DailyChecklist";
import { CoachingAlert } from "@/components/daily/CoachingAlert";
import { useActiveGoal } from "@/hooks/useGoals";
import { useToday } from "@/hooks/useToday";

export function HomePage() {
  const { data: goal, isLoading } = useActiveGoal();
  const { data: dailyLogs } = useToday();
  const today = format(new Date(), "yyyy-MM-dd");

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <Target className="w-12 h-12 text-muted-foreground" />
        <h2 className="text-lg font-medium">No goal yet</h2>
        <p className="text-muted-foreground text-sm">
          Create your goal to get started with AI coaching
        </p>
        <Link to="/goals/new">
          <Button className="gap-2">
            <Plus className="w-4 h-4" /> New Goal
          </Button>
        </Link>
      </div>
    );
  }

  const log = dailyLogs?.find(
    (l) => l.goal_id === goal.id && l.date === today
  );

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-xl font-semibold">Today</h1>
      <CoachingAlert goalId={goal.id} />
      <DailyChecklist goal={goal} log={log} />
    </div>
  );
}
