import { useRef, useEffect } from "react";
import type { ChatMessage } from "@/types/coaching";
import { format } from "date-fns";
import { Search, TrendingUp, ListChecks, Target } from "lucide-react";
import { TypingIndicator } from "./TypingIndicator";

interface ChatMessagesProps {
  messages: ChatMessage[];
  isTyping?: boolean;
}

export function ChatMessages({ messages, isTyping = false }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isTyping]);

  const getToolIcon = (toolName: string) => {
    switch (toolName) {
      case "get_active_habits":
        return <ListChecks className="w-3 h-3" />;
      case "get_trackers":
        return <Target className="w-3 h-3" />;
      case "get_habit_performance":
      case "get_tracker_trend":
        return <TrendingUp className="w-3 h-3" />;
      default:
        return <Search className="w-3 h-3" />;
    }
  };

  return (
    <div ref={scrollRef} className="flex-1 pr-4 overflow-y-auto">
      <div className="space-y-4 pb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"
              }`}
          >
            {msg.role !== "user" && (
              <span className="text-xs font-medium text-primary mb-1 ml-1">
                Priya
              </span>
            )}

            {/* Show tool calls before the message (AI is "thinking") */}
            {msg.role === "assistant" && msg.tool_calls && msg.tool_calls.length > 0 && (
              <div className="max-w-[80%] space-y-2 mb-2">
                {msg.tool_calls.map((tool, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 px-3 py-2 rounded-md bg-primary/10 text-primary text-xs"
                  >
                    {getToolIcon(tool.name)}
                    <span className="italic">{tool.description}</span>
                  </div>
                ))}
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
                }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <p
                className={`text-xs mt-1 ${msg.role === "user"
                    ? "text-primary-foreground/60"
                    : "text-muted-foreground"
                  }`}
              >
                {format(new Date(msg.timestamp), "h:mm a")}
              </p>
            </div>
          </div>
        ))}
        {isTyping && <TypingIndicator />}
      </div>
    </div>
  );
}
