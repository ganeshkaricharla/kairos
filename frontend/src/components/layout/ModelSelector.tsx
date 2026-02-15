import { useState, useRef, useEffect } from "react";
import { Bot, Check, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useModels, useSelectedModel, useSelectModel } from "@/hooks/useModels";

export function ModelSelector() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  const { data: models, isLoading } = useModels(search);
  const { data: selected } = useSelectedModel();
  const selectModel = useSelectModel();

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selectedId = selected?.model_id;
  const displayName = selectedId
    ? selectedId.split("/").pop()
    : "No model";

  return (
    <div className="relative" ref={ref}>
      <Button
        variant="outline"
        size="sm"
        className="gap-2 text-xs max-w-48"
        onClick={() => setOpen(!open)}
      >
        <Bot className="w-3 h-3 shrink-0" />
        <span className="truncate">{displayName}</span>
      </Button>

      {open && (
        <div className="absolute right-0 top-full mt-1 w-96 bg-card border rounded-lg shadow-lg z-50">
          <div className="p-2 border-b">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 w-3.5 h-3.5 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search models..."
                className="pl-8 h-8 text-sm"
                autoFocus
              />
            </div>
          </div>

          <ScrollArea className="h-72">
            {isLoading ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                Loading models...
              </div>
            ) : !models?.length ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No models found
              </div>
            ) : (
              <div className="p-1">
                {models.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => {
                      selectModel.mutate(model.id);
                      setOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-md hover:bg-accent flex items-center gap-2 group"
                  >
                    <div className="w-4 shrink-0">
                      {model.id === selectedId && (
                        <Check className="w-3.5 h-3.5 text-primary" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {model.name}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {model.id}
                      </p>
                    </div>
                    {model.context_length && (
                      <Badge variant="secondary" className="text-xs shrink-0">
                        {Math.round(model.context_length / 1000)}k
                      </Badge>
                    )}
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      )}
    </div>
  );
}
