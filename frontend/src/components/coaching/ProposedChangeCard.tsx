import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, X } from "lucide-react";
import type { ProposedChange } from "@/types/coaching";

interface ProposedChangeCardProps {
  change: ProposedChange;
  index: number;
  onAccept: () => void;
  onReject: () => void;
}

const typeLabels: Record<string, string> = {
  add_habit: "New Habit",
  swap_habit: "Swap Habit",
  upgrade_intensity: "Level Up",
  downgrade_intensity: "Ease Up",
  pause_habit: "Pause",
  add_tracker: "New Tracker",
};

export function ProposedChangeCard({
  change,
  onAccept,
  onReject,
}: ProposedChangeCardProps) {
  const decided = change.accepted === true || change.accepted === false;

  return (
    <Card
      className={`${
        decided ? "opacity-60" : ""
      }`}
    >
      <CardContent className="pt-4 pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <Badge variant="outline" className="mb-2">
              {typeLabels[change.type] ?? change.type}
            </Badge>
            <p className="text-sm">{change.description}</p>
          </div>
          {decided ? (
            <Badge variant={change.accepted ? "default" : "secondary"}>
              {change.accepted ? "Accepted" : "Rejected"}
            </Badge>
          ) : (
            <div className="flex gap-1 shrink-0">
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8 text-green-600 hover:bg-green-50"
                onClick={onAccept}
              >
                <Check className="w-4 h-4" />
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="h-8 w-8 text-red-600 hover:bg-red-50"
                onClick={onReject}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
