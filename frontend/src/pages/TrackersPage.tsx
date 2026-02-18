import { useActiveGoal } from "@/hooks/useGoals";
import { useTrackers } from "@/hooks/useTrackers";
import { TrackerChart } from "@/components/trackers/TrackerChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { dailyLogsApi } from "@/api/dailyLogs";
import { format, subDays } from "date-fns";
import { Plus, TrendingUp, TrendingDown } from "lucide-react";
import { Link } from "react-router-dom";

function TrackersContent({ goalId }: { goalId: string }) {
  const { data: trackers, isLoading } = useTrackers(goalId);

  const last14 = Array.from({ length: 14 }, (_, i) =>
    format(subDays(new Date(), 13 - i), "yyyy-MM-dd")
  );

  const { data: logs } = useQuery({
    queryKey: ["tracker-logs", goalId, last14[0]],
    queryFn: async () => {
      const all = await Promise.all(last14.map((d) => dailyLogsApi.get(d)));
      return all.flat().filter((log) => log.goal_id === goalId);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading trackers...</p>
      </div>
    );
  }

  if (!trackers || trackers.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">
              No trackers yet. Your AI coach will suggest metrics to track based on your goal.
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

  // Calculate tracker stats
  const trackerStats = trackers.map((tracker) => {
    const values = last14
      .map((date) => {
        const log = logs?.find((l) => l.date === date);
        const entry = log?.tracker_entries.find((e) => e.tracker_id === tracker.id);
        return entry?.value;
      })
      .filter((v): v is number => v !== undefined);

    const latestValue = values[values.length - 1];
    const firstValue = values[0];
    const average = values.length > 0
      ? values.reduce((sum, v) => sum + v, 0) / values.length
      : 0;

    let trend: "up" | "down" | "stable" = "stable";
    if (values.length >= 2 && latestValue !== undefined && firstValue !== undefined) {
      if (latestValue > firstValue) trend = "up";
      else if (latestValue < firstValue) trend = "down";
    }

    return { tracker, latestValue, average, trend, dataPoints: values.length };
  });

  return (
    <div className="space-y-6">
      {/* Tracker Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {trackerStats.map(({ tracker, latestValue, average, trend, dataPoints }) => (
          <Card key={tracker.id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-base font-medium">
                    {tracker.name}
                  </CardTitle>
                  {tracker.is_primary && (
                    <Badge variant="default" className="mt-1">
                      Primary Metric
                    </Badge>
                  )}
                </div>
                {trend !== "stable" && (
                  <div className={trend === "up" ? "text-green-500" : "text-red-500"}>
                    {trend === "up" ? (
                      <TrendingUp className="w-5 h-5" />
                    ) : (
                      <TrendingDown className="w-5 h-5" />
                    )}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {latestValue !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Latest:</span>
                    <span className="text-lg font-semibold">
                      {latestValue} {tracker.unit}
                    </span>
                  </div>
                )}
                {dataPoints > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">14-day avg:</span>
                    <span className="font-medium">
                      {average.toFixed(1)} {tracker.unit}
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Data points:</span>
                  <span>{dataPoints} / 14 days</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tracker Charts */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Trends</h2>
        {trackers.map((tracker) => (
          <TrackerChart key={tracker.id} tracker={tracker} logs={logs || []} />
        ))}
      </div>
    </div>
  );
}

export function TrackersPage() {
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
          <h1 className="text-2xl font-bold">Trackers</h1>
          <p className="text-muted-foreground">
            Monitor your metrics for: {goal.title}
          </p>
          {goal.primary_metric_name && (
            <p className="text-sm text-muted-foreground mt-1">
              Primary metric: <span className="font-medium text-foreground">
                {goal.primary_metric_name} ({goal.primary_metric_unit})
              </span>
            </p>
          )}
        </div>
      </div>

      <TrackersContent goalId={goal.id} />
    </div>
  );
}
