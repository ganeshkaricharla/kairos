import { useActiveGoal } from "@/hooks/useGoals";
import { useHabits } from "@/hooks/useHabits";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { dailyLogsApi } from "@/api/dailyLogs";
import { format, subDays } from "date-fns";
import { Plus } from "lucide-react";
import { Link } from "react-router-dom";

function HabitsContent({ goalId }: { goalId: string }) {
  const { data: habits, isLoading } = useHabits(goalId, "active");

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

  // Calculate streaks and completion rates
  const habitStats =
    habits?.map((habit) => {
      // Filter dates to only count from habit activation onwards
      const activatedDate = habit.activated_at
        ? format(new Date(habit.activated_at), "yyyy-MM-dd")
        : null;

      const relevantDates = last14.filter((date) => {
        if (!activatedDate) return true;
        return date >= activatedDate;
      });

      let streak = 0;

      // Calculate streak (consecutive days from today backwards)
      for (let i = relevantDates.length - 1; i >= 0; i--) {
        const log = logs?.find((l) => l.date === relevantDates[i]);
        const completed = log?.habit_completions.some(
          (c) => c.habit_id === habit.id && c.completed
        );
        if (completed) {
          streak++;
        } else if (i === relevantDates.length - 1) {
          // If today is not done, streak is 0
          break;
        } else {
          break;
        }
      }

      // Count total completions only in relevant days
      const totalCompletions = relevantDates.reduce((count, date) => {
        const log = logs?.find((l) => l.date === date);
        const completed = log?.habit_completions.some(
          (c) => c.habit_id === habit.id && c.completed
        );
        return count + (completed ? 1 : 0);
      }, 0);

      const completionRate = relevantDates.length > 0
        ? Math.round((totalCompletions / relevantDates.length) * 100)
        : 0;

      return { habit, streak, completionRate };
    }) ?? [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading habits...</p>
      </div>
    );
  }

  if (!habits || habits.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">
              No habits yet. Your AI coach will suggest personalized habits based on your goal.
            </p>
            <Button variant="outline">
              <Plus className="w-4 h-4 mr-2" />
              Go to Coaching
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Habit Cards with Streaks */}
      <div className="grid gap-4 md:grid-cols-2">
        {habitStats.map(({ habit, streak, completionRate }) => (
          <Card key={habit.id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-base font-medium">
                    {habit.title}
                  </CardTitle>
                  {habit.description && (
                    <p className="text-sm text-muted-foreground mt-1">
                      {habit.description}
                    </p>
                  )}
                </div>
                <Badge variant={streak > 0 ? "default" : "secondary"} className="ml-2">
                  🔥 {streak}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Completion rate:</span>
                  <span className="font-medium">{completionRate}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Difficulty:</span>
                  <Badge variant="outline" className="capitalize">
                    {habit.difficulty}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 14-Day Completion Grid */}
      <Card>
        <CardHeader>
          <CardTitle>Completion History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {habits.map((habit) => {
              // Filter dates to only show from habit activation onwards
              const activatedDate = habit.activated_at
                ? format(new Date(habit.activated_at), "yyyy-MM-dd")
                : null;

              const today = format(new Date(), "yyyy-MM-dd");
              const relevantDates = last14.filter((date) => {
                if (!activatedDate) return true; // Show all if no activation date
                return date >= activatedDate; // Only show from activation onwards
              });

              // Check if habit starts in the future
              const startsInFuture = activatedDate && activatedDate > today;

              return (
                <div key={habit.id}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium">{habit.title}</p>
                    {startsInFuture && (
                      <Badge variant="outline" className="text-xs">
                        Starts {format(new Date(activatedDate), "MMM d")}
                      </Badge>
                    )}
                  </div>

                  {relevantDates.length === 0 ? (
                    <div className="text-sm text-muted-foreground py-4 text-center bg-muted rounded">
                      This habit will start on {format(new Date(activatedDate!), "MMMM d, yyyy")}
                    </div>
                  ) : (
                    <div className="flex gap-1">
                      {relevantDates.map((date) => {
                        const log = logs?.find((l) => l.date === date);
                        const done = log?.habit_completions.some(
                          (c) => c.habit_id === habit.id && c.completed
                        );
                        return (
                          <div
                            key={date}
                            className={`flex-1 h-12 rounded text-xs flex flex-col items-center justify-center ${
                              done
                                ? "bg-green-500 text-white"
                                : "bg-muted text-muted-foreground"
                            }`}
                            title={date}
                          >
                            <div className="font-medium">{parseInt(date.slice(8))}</div>
                            <div className="text-[10px] opacity-75">
                              {format(new Date(date), "EEE")}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <div className="flex gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-muted rounded"></div>
          <span>Not completed</span>
        </div>
      </div>
    </div>
  );
}

export function HabitsPage() {
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
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-muted-foreground">No active goal found.</p>
        <Link to="/goals/new">
          <Button>Create a Goal</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Habits</h1>
          <p className="text-muted-foreground">
            Track your daily habits for: {goal.title}
          </p>
        </div>
      </div>

      <HabitsContent goalId={goal.id} />
    </div>
  );
}
