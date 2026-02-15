import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("");

  function handleSend() {
    const trimmed = message.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setMessage("");
  }

  return (
    <div className="flex gap-2 pt-3 border-t">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder="Reply to your coach..."
        className="resize-none min-h-[44px] max-h-32"
        rows={1}
        disabled={disabled}
      />
      <Button
        size="icon"
        onClick={handleSend}
        disabled={disabled || !message.trim()}
        className="shrink-0 h-11 w-11"
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  );
}
