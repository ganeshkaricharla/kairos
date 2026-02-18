export function TypingIndicator() {
  return (
    <div className="flex flex-col items-start">
      <span className="text-xs font-medium text-primary mb-1 ml-1">
        Priya is typing...
      </span>
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-muted">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-muted-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}
