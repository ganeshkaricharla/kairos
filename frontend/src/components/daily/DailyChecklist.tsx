import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { HabitItem } from "@/components/habits/HabitItem";
import { TrackerInput } from "@/components/trackers/TrackerInput";
import { CompletionRing } from "./CompletionRing";
import { useToggleHabit, useLogTracker } from "@/hooks/useToday";
import type { Goal } from "@/types/goal";
import type { DailyLog } from "@/types/dailyLog";
import { Link } from "react-router-dom";

interface DailyChecklistProps {
  goal: Goal;
  log?: DailyLog;
}

export function DailyChecklist({ goal, log }: DailyChecklistProps) {
  const toggleHabit = useToggleHabit();
  const logTracker = useLogTracker();

  const habits = goal.habits ?? [];
  const trackers = goal.trackers ?? [];
  const completions = log?.habit_completions ?? [];
  const entries = log?.tracker_entries ?? [];

  const completedCount = habits.filter((h) =>
    completions.some((c) => c.habit_id === h.id && c.completed)
  ).length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <Link to={`/goals/${goal.id}`} className="hover:underline">
            <CardTitle className="text-base">{goal.title}</CardTitle>
          </Link>
          <CompletionRing completed={completedCount} total={habits.length} />
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        {habits.map((habit) => {
          const completion = completions.find(
            (c) => c.habit_id === habit.id
          );
          return (
            <HabitItem
              key={habit.id}
              habit={habit}
              completed={completion?.completed ?? false}
              disabled={toggleHabit.isPending}
              onToggle={() =>
                toggleHabit.mutate({
                  goalId: goal.id,
                  habitId: habit.id,
                })
              }
            />
          );
        })}

        {trackers.length > 0 && (
          <>
            <Separator className="my-3" />
            {trackers.map((tracker) => {
              const entry = entries.find(
                (e) => e.tracker_id === tracker.id
              );
              return (
                <TrackerInput
                  key={tracker.id}
                  tracker={tracker}
                  currentValue={entry?.value}
                  onLog={(value) =>
                    logTracker.mutate({
                      goalId: goal.id,
                      trackerId: tracker.id,
                      value,
                    })
                  }
                />
              );
            })}
          </>
        )}
      </CardContent>
    </Card>
  );
}
