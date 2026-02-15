import { useActiveGoal } from "@/hooks/useGoals";
import { useHabits } from "@/hooks/useHabits";
import { useTrackers } from "@/hooks/useTrackers";
import { TrackerChart } from "@/components/trackers/TrackerChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { dailyLogsApi } from "@/api/dailyLogs";
import { format, subDays } from "date-fns";

function GoalProgress({ goalId }: { goalId: string }) {
  const { data: habits } = useHabits(goalId, "active");
  const { data: trackers } = useTrackers(goalId);

  const last14 = Array.from({ length: 14 }, (_, i) =>
    format(subDays(new Date(), 13 - i), "yyyy-MM-dd")
  );

  const { data: logs } = useQuery({
    queryKey: ["progress-logs", goalId, last14[0]],
    queryFn: async () => {
      const all = await Promise.all(last14.map((d) => dailyLogsApi.get(d)));
      return all.flat().filter((log) => log.goal_id === goalId);
    },
  });

  // Calculate streaks per habit
  const habitStreaks =
    habits?.map((habit) => {
      let streak = 0;
      for (let i = last14.length - 1; i >= 0; i--) {
        const log = logs?.find((l) => l.date === last14[i]);
        const completed = log?.habit_completions.some(
          (c) => c.habit_id === habit.id && c.completed
        );
        if (completed) {
          streak++;
        } else {
          break;
        }
      }
      return { habit, streak };
    }) ?? [];

  return (
    <div className="space-y-4">
      {/* Streaks */}
      {habitStreaks.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Current Streaks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {habitStreaks.map(({ habit, streak }) => (
                <div
                  key={habit.id}
                  className="flex items-center justify-between"
                >
                  <span className="text-sm">{habit.title}</span>
                  <Badge
                    variant={streak > 0 ? "default" : "secondary"}
                  >
                    {streak} day{streak !== 1 ? "s" : ""}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Habit Completion Grid */}
      {habits && habits.length > 0 && logs && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">14-Day Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {habits.map((habit) => (
                <div key={habit.id}>
                  <p className="text-xs text-muted-foreground mb-1">
                    {habit.title}
                  </p>
                  <div className="flex gap-1">
                    {last14.map((date) => {
                      const log = logs.find((l) => l.date === date);
                      const done = log?.habit_completions.some(
                        (c) => c.habit_id === habit.id && c.completed
                      );
                      return (
                        <div
                          key={date}
                          className={`w-6 h-6 rounded-sm text-xs flex items-center justify-center ${
                            done
                              ? "bg-green-500 text-white"
                              : "bg-muted text-muted-foreground"
                          }`}
                          title={date}
                        >
                          {parseInt(date.slice(8))}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tracker Charts */}
      {trackers &&
        logs &&
        trackers.map((tracker) => (
          <TrackerChart key={tracker.id} tracker={tracker} logs={logs} />
        ))}
    </div>
  );
}

export function ProgressPage() {
  const { data: goal, isLoading } = useActiveGoal();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">No active goal to show progress for.</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-xl font-semibold">Progress</h1>
      <h2 className="text-lg font-medium">{goal.title}</h2>
      <GoalProgress goalId={goal.id} />
    </div>
  );
}
