import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface GoalFormProps {
  onSubmit: (data: {
    title: string;
    description: string;
    target_date?: string;
  }) => void;
  loading?: boolean;
}

export function GoalForm({ onSubmit, loading }: GoalFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [targetDate, setTargetDate] = useState("");

  return (
    <Card className="max-w-lg mx-auto">
      <CardHeader>
        <CardTitle>What do you want to achieve?</CardTitle>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit({
              title,
              description,
              target_date: targetDate || undefined,
            });
          }}
          className="space-y-4"
        >
          <div>
            <label className="text-sm font-medium mb-1 block">Goal Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder='e.g., "Get fit and lose 10kg"'
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">
              Describe your goal in detail
            </label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does success look like? What have you tried before? Any constraints?"
              rows={4}
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">
              Target Date (optional)
            </label>
            <Input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Creating goal..." : "Create Goal & Get AI Plan"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
