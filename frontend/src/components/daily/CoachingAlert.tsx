import { Link } from "react-router-dom";
import { MessageCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useActiveCoaching } from "@/hooks/useCoaching";

export function CoachingAlert({ goalId }: { goalId: string }) {
  const { data: session } = useActiveCoaching(goalId);

  if (!session) return null;

  return (
    <div className="rounded-lg border border-primary/20 bg-primary/5 p-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
          <MessageCircle className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-sm">Priya wants to check in with you</p>
          <p className="text-xs text-muted-foreground">
            Let's talk about your progress and next steps
          </p>
        </div>
      </div>
      <Link to={`/goals/${goalId}/coach`}>
        <Button size="sm" className="gap-1">
          Chat <ArrowRight className="w-3 h-3" />
        </Button>
      </Link>
    </div>
  );
}
