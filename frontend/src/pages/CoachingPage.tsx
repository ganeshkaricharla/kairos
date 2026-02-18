import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatMessages } from "@/components/coaching/ChatMessages";
import { ChatInput } from "@/components/coaching/ChatInput";
import {
  useActiveCoaching,
  useStartCoaching,
  useSendMessage,
  useResolveSession,
} from "@/hooks/useCoaching";

export function CoachingPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: session, isLoading } = useActiveCoaching(id!);
  const startCoaching = useStartCoaching();
  const sendMessage = useSendMessage();
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
        <p className="text-muted-foreground">No active conversation with Priya</p>
        {startCoaching.error && (
          <div className="text-sm text-destructive bg-destructive/10 px-4 py-2 rounded-md">
            {(startCoaching.error as any)?.response?.data?.detail || startCoaching.error.message}
          </div>
        )}
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
              Starting chat...
            </>
          ) : (
            "Start Chatting with Priya"
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

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Link to={`/goals/${id}`}>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <h1 className="text-lg font-semibold">Chat with Priya</h1>
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

      {/* Chat area */}
      <ChatMessages messages={session.messages} isTyping={sendMessage.isPending} />

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
  );
}
