import { Check } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { Habit } from "@/types/habit";

interface HabitItemProps {
  habit: Habit;
  completed: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export function HabitItem({ habit, completed, onToggle, disabled }: HabitItemProps) {
  return (
    <div className="flex items-center gap-3 py-2">
      <button
        onClick={onToggle}
        disabled={disabled}
        className={`w-6 h-6 rounded-md border-2 flex items-center justify-center transition-colors shrink-0 ${
          completed
            ? "bg-primary border-primary text-primary-foreground"
            : "border-muted-foreground/30 hover:border-primary"
        } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
      >
        {completed && <Check className="w-4 h-4" />}
      </button>

      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex-1 min-w-0">
            <p
              className={`text-sm ${
                completed ? "line-through text-muted-foreground" : ""
              }`}
            >
              {habit.title}
            </p>
            {habit.time_of_day && (
              <p className="text-xs text-muted-foreground">
                {habit.time_of_day}
                {habit.duration_minutes
                  ? ` - ${habit.duration_minutes} min`
                  : ""}
              </p>
            )}
          </div>
        </TooltipTrigger>
        {habit.reasoning && (
          <TooltipContent side="right" className="max-w-xs">
            <p className="text-xs">{habit.reasoning}</p>
          </TooltipContent>
        )}
      </Tooltip>
    </div>
  );
}
