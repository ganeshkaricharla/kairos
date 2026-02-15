import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DailyLog } from "@/types/dailyLog";
import type { Tracker } from "@/types/tracker";

interface TrackerChartProps {
  tracker: Tracker;
  logs: DailyLog[];
}

export function TrackerChart({ tracker, logs }: TrackerChartProps) {
  const data = logs
    .map((log) => {
      const entry = log.tracker_entries.find(
        (e) => e.tracker_id === tracker.id
      );
      return entry
        ? { date: log.date.slice(5), value: entry.value }
        : null;
    })
    .filter(Boolean);

  if (data.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">
          {tracker.name}{" "}
          <span className="text-muted-foreground font-normal">
            ({tracker.unit})
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
