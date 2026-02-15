import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import type { Tracker } from "@/types/tracker";

interface TrackerInputProps {
  tracker: Tracker;
  currentValue?: number;
  onLog: (value: number) => void;
}

export function TrackerInput({
  tracker,
  currentValue,
  onLog,
}: TrackerInputProps) {
  const [value, setValue] = useState(
    currentValue?.toString() ?? ""
  );
  const [saved, setSaved] = useState(false);

  function handleSubmit() {
    const num = parseFloat(value);
    if (isNaN(num)) return;
    onLog(num);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="flex items-center gap-2 py-1">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{tracker.name}</p>
      </div>
      <div className="flex items-center gap-1">
        <Input
          type="number"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setSaved(false);
          }}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          className="w-20 h-8 text-sm"
          placeholder="0"
        />
        <span className="text-xs text-muted-foreground w-12 truncate">
          {tracker.unit}
        </span>
        <Button
          size="icon"
          variant={saved ? "default" : "outline"}
          className="h-8 w-8"
          onClick={handleSubmit}
        >
          <Check className="w-3 h-3" />
        </Button>
      </div>
    </div>
  );
}
