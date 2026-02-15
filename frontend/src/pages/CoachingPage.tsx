import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessages } from "@/components/coaching/ChatMessages";
import { ChatInput } from "@/components/coaching/ChatInput";
import { ProposedChangeCard } from "@/components/coaching/ProposedChangeCard";
import {
  useActiveCoaching,
  useStartCoaching,
  useSendMessage,
  useAcceptChange,
  useRejectChange,
  useResolveSession,
} from "@/hooks/useCoaching";

export function CoachingPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: session, isLoading } = useActiveCoaching(id!);
  const startCoaching = useStartCoaching();
  const sendMessage = useSendMessage();
  const acceptChange = useAcceptChange();
  const rejectChange = useRejectChange();
  const resolveSession = useResolveSession();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="max-w-2xl mx-auto flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-muted-foreground">No active coaching session</p>
        <Button
          onClick={() =>
            startCoaching.mutate({
              goalId: id!,
              trigger: "user_initiated",
            })
          }
          disabled={startCoaching.isPending}
        >
          {startCoaching.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Starting review...
            </>
          ) : (
            "Start a Review Session"
          )}
        </Button>
      </div>
    );
  }

  function handleResolve() {
    resolveSession.mutate(
      { sessionId: session!.id, goalId: id! },
      { onSuccess: () => navigate(`/goals/${id}`) }
    );
  }

  const pendingChanges = session.proposed_changes.filter(
    (c) => c.accepted !== true && c.accepted !== false
  );
  const decidedChanges = session.proposed_changes.filter(
    (c) => c.accepted === true || c.accepted === false
  );
  const hasChanges = session.proposed_changes.length > 0;

  return (
    <div className="flex gap-6 h-full min-h-0 overflow-hidden">
      {/* Chat area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Link to={`/goals/${id}`}>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <ArrowLeft className="w-4 h-4" />
              </Button>
            </Link>
            <h1 className="text-lg font-semibold">Coaching Session</h1>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleResolve}
            disabled={resolveSession.isPending}
          >
            End Session
          </Button>
        </div>

        <ChatMessages messages={session.messages} />

        <ChatInput
          onSend={(message) =>
            sendMessage.mutate({
              sessionId: session.id,
              message,
              goalId: id!,
            })
          }
          disabled={sendMessage.isPending}
        />
      </div>

      {/* Sidebar for proposed changes — sticky so it stays visible while chat scrolls */}
      {hasChanges && (
        <div className="w-80 shrink-0 flex flex-col border-l pl-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-primary" />
            <h2 className="text-sm font-semibold">Proposed Changes</h2>
          </div>

          <ScrollArea className="flex-1">
            <div className="space-y-3 pr-2">
              {pendingChanges.length > 0 && (
                <>
                  {pendingChanges.map((change, i) => {
                    const originalIndex = session.proposed_changes.indexOf(change);
                    return (
                      <ProposedChangeCard
                        key={originalIndex}
                        change={change}
                        index={originalIndex}
                        onAccept={() =>
                          acceptChange.mutate({
                            sessionId: session.id,
                            index: originalIndex,
                            goalId: id!,
                          })
                        }
                        onReject={() =>
                          rejectChange.mutate({
                            sessionId: session.id,
                            index: originalIndex,
                            goalId: id!,
                          })
                        }
                      />
                    );
                  })}
                </>
              )}

              {decidedChanges.length > 0 && (
                <>
                  {pendingChanges.length > 0 && (
                    <div className="border-t my-3" />
                  )}
                  <p className="text-xs text-muted-foreground mb-2">Decided</p>
                  {decidedChanges.map((change) => {
                    const originalIndex = session.proposed_changes.indexOf(change);
                    return (
                      <ProposedChangeCard
                        key={originalIndex}
                        change={change}
                        index={originalIndex}
                        onAccept={() => {}}
                        onReject={() => {}}
                      />
                    );
                  })}
                </>
              )}
            </div>
          </ScrollArea>
        </div>
      )}
    </div>
  );
}
