import { useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage } from "@/types/coaching";
import { format } from "date-fns";

interface ChatMessagesProps {
  messages: ChatMessage[];
}

export function ChatMessages({ messages }: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <ScrollArea className="flex-1 pr-4">
      <div className="space-y-4 pb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <p
                className={`text-xs mt-1 ${
                  msg.role === "user"
                    ? "text-primary-foreground/60"
                    : "text-muted-foreground"
                }`}
              >
                {format(new Date(msg.timestamp), "h:mm a")}
              </p>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
