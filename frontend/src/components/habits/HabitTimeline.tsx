import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight } from "lucide-react";
import type { Habit } from "@/types/habit";
import { format } from "date-fns";

interface HabitTimelineProps {
  habits: Habit[];
}

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  swapped: "bg-yellow-100 text-yellow-800",
  paused: "bg-gray-100 text-gray-800",
  completed: "bg-blue-100 text-blue-800",
};

export function HabitTimeline({ habits }: HabitTimelineProps) {
  const sorted = [...habits].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">Habit History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {sorted.map((habit) => (
            <div
              key={habit.id}
              className="flex items-center gap-3 text-sm"
            >
              <div className="w-2 h-2 rounded-full bg-primary shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{habit.title}</span>
                  <Badge
                    variant="outline"
                    className={statusColors[habit.status] ?? ""}
                  >
                    {habit.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {format(new Date(habit.created_at), "MMM d, yyyy")}
                  {habit.replaced_by && (
                    <span className="inline-flex items-center gap-1 ml-2">
                      <ArrowRight className="w-3 h-3" /> replaced
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
