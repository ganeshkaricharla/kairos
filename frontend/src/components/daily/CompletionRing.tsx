interface CompletionRingProps {
  completed: number;
  total: number;
  size?: number;
}

export function CompletionRing({
  completed,
  total,
  size = 48,
}: CompletionRingProps) {
  const pct = total > 0 ? completed / total : 0;
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - pct * circumference;

  return (
    <div className="flex items-center gap-2">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={3}
          className="text-muted"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={3}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={pct === 1 ? "text-green-500" : "text-primary"}
        />
      </svg>
      <span className="text-sm font-medium">
        {completed}/{total}
      </span>
    </div>
  );
}
