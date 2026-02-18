import { useParams, Link } from "react-router-dom";
import { MessageCircle, Plus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { TrackerChart } from "@/components/trackers/TrackerChart";
import { HabitTimeline } from "@/components/habits/HabitTimeline";
import { useGoal } from "@/hooks/useGoals";
import { useHabits } from "@/hooks/useHabits";
import { useTrackers } from "@/hooks/useTrackers";
import { useActiveCoaching, useStartCoaching } from "@/hooks/useCoaching";
import { useQuery } from "@tanstack/react-query";
import { dailyLogsApi } from "@/api/dailyLogs";
import { format, subDays } from "date-fns";

export function GoalDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: goal, isLoading } = useGoal(id!);
  const { data: allHabits } = useHabits(id!, undefined);
  const { data: trackers } = useTrackers(id!);
  const { data: coachingSession } = useActiveCoaching(id!);
  const startCoaching = useStartCoaching();

  // Fetch recent daily logs for charts
  const last14 = Array.from({ length: 14 }, (_, i) =>
    format(subDays(new Date(), 13 - i), "yyyy-MM-dd")
  );

  const { data: recentLogs } = useQuery({
    queryKey: ["daily-logs-range", id, last14[0], last14[last14.length - 1]],
    queryFn: async () => {
      const all = await Promise.all(last14.map((d) => dailyLogsApi.get(d)));
      return all
        .flat()
        .filter((log) => log.goal_id === id);
    },
    enabled: !!id,
  });

  if (isLoading || !goal) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  const activeHabits = allHabits?.filter((h) => h.status === "active") ?? [];
  const pastHabits =
    allHabits?.filter((h) => h.status !== "active") ?? [];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold">{goal.title}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {goal.description}
          </p>
          <Badge variant="outline" className="mt-2">
            {goal.ai_context.current_phase.replace(/_/g, " ")}
          </Badge>
        </div>
        <div className="flex gap-2">
          {coachingSession ? (
            <Link to={`/goals/${id}/coach`}>
              <Button size="sm" className="gap-1">
                <MessageCircle className="w-4 h-4" />
                Chat with Priya
              </Button>
            </Link>
          ) : (
            <Button
              size="sm"
              variant="outline"
              className="gap-1"
              onClick={() =>
                startCoaching.mutate({
                  goalId: id!,
                  trigger: "user_initiated",
                })
              }
              disabled={startCoaching.isPending}
            >
              <Plus className="w-4 h-4" />
              Talk to Priya
            </Button>
          )}
        </div>
      </div>

      {goal.ai_context.summary && (
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground italic">
              {goal.ai_context.summary}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Active Habits */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Active Habits</CardTitle>
        </CardHeader>
        <CardContent>
          {activeHabits.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No active habits yet.
            </p>
          ) : (
            <div className="space-y-2">
              {activeHabits.map((habit) => (
                <div key={habit.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">{habit.title}</span>
                    <Badge variant="secondary">{habit.difficulty}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {habit.description}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tracker Charts */}
      {trackers && trackers.length > 0 && recentLogs && (
        <div className="space-y-4">
          {trackers.map((tracker) => (
            <TrackerChart
              key={tracker.id}
              tracker={tracker}
              logs={recentLogs}
            />
          ))}
        </div>
      )}

      {/* Past Habits */}
      {pastHabits.length > 0 && (
        <>
          <Separator />
          <HabitTimeline habits={pastHabits} />
        </>
      )}
    </div>
  );
}
