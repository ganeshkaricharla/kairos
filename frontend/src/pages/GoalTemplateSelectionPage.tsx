import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { goalTemplatesApi, type GoalTemplate } from "@/api/goalTemplates";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateGoal } from "@/hooks/useGoals";

export function GoalTemplateSelectionPage() {
  const navigate = useNavigate();
  const [selectedTemplate, setSelectedTemplate] = useState<GoalTemplate | null>(null);
  const [questionnaireResponses, setQuestionnaireResponses] = useState<Record<string, string>>({});
  const [initialValue, setInitialValue] = useState("");
  const [targetValue, setTargetValue] = useState("");

  const { data: templates, isLoading } = useQuery({
    queryKey: ["goalTemplates"],
    queryFn: goalTemplatesApi.list,
  });

  const createGoal = useCreateGoal();

  function handleQuestionnaireChange(questionId: string, value: string) {
    setQuestionnaireResponses(prev => ({ ...prev, [questionId]: value }));
  }

  async function handleCreateGoal() {
    if (!selectedTemplate) return;

    const goal = await createGoal.mutateAsync({
      template_id: selectedTemplate.id,
      description: "User completed questionnaire", // Placeholder description
      initial_value: initialValue ? parseFloat(initialValue) : undefined,
      target_value: targetValue ? parseFloat(targetValue) : undefined,
      questionnaire_responses: questionnaireResponses,
    });

    // Redirect to coaching
    navigate(`/goals/${goal.id}/coach`);
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading goal templates...</p>
      </div>
    );
  }

  if (selectedTemplate) {
    // Show customization form
    return (
      <div className="max-w-2xl mx-auto p-6">
        <Button
          variant="ghost"
          onClick={() => setSelectedTemplate(null)}
          className="mb-4"
        >
          ← Back to templates
        </Button>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <span className="text-4xl">{selectedTemplate.icon}</span>
              <div>
                <CardTitle>{selectedTemplate.name}</CardTitle>
                <CardDescription>{selectedTemplate.description}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">
                Primary Metric: <span className="text-primary">{selectedTemplate.primary_metric_name} ({selectedTemplate.primary_metric_unit})</span>
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                This metric will be tracked daily to measure your progress.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-1">Tell us about yourself</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Answer these questions to help us personalize your plan.
                </p>
              </div>

              {selectedTemplate.questionnaire && selectedTemplate.questionnaire.map((question) => (
                <div key={question.id} className="space-y-2">
                  <label className="text-sm font-medium block">
                    {question.question}
                  </label>
                  <select
                    className="w-full p-2 border rounded-md bg-background"
                    value={questionnaireResponses[question.id] || ""}
                    onChange={(e) => handleQuestionnaireChange(question.id, e.target.value)}
                    required
                  >
                    <option value="">Select an option...</option>
                    {question.options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Initial {selectedTemplate.primary_metric_name} ({selectedTemplate.primary_metric_unit})
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={initialValue}
                  onChange={(e) => setInitialValue(e.target.value)}
                  placeholder={`e.g., 75`}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Your current starting point
                </p>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Target {selectedTemplate.primary_metric_name} ({selectedTemplate.primary_metric_unit})
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={targetValue}
                  onChange={(e) => setTargetValue(e.target.value)}
                  placeholder={`e.g., 65`}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Your desired outcome
                </p>
              </div>
            </div>

            <div className="bg-muted p-4 rounded-lg">
              <p className="text-sm font-medium mb-2">Example habits for this goal:</p>
              <ul className="text-sm text-muted-foreground space-y-1">
                {selectedTemplate.example_habits.map((habit, i) => (
                  <li key={i}>• {habit}</li>
                ))}
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                Note: Priya will suggest personalized habits based on your answers.
              </p>
            </div>

            <Button
              onClick={handleCreateGoal}
              className="w-full"
              disabled={
                !initialValue ||
                !targetValue ||
                Object.keys(questionnaireResponses).length !== selectedTemplate.questionnaire?.length ||
                createGoal.isPending
              }
            >
              {createGoal.isPending ? "Creating your plan..." : "Create Goal & Get Plan"}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show template selection
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Choose Your Goal</h1>
        <p className="text-muted-foreground">
          Select a goal template to get started. Each template has a proven tracking system.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates?.map((template) => (
          <Card
            key={template.id}
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => setSelectedTemplate(template)}
          >
            <CardHeader>
              <div className="text-4xl mb-2">{template.icon}</div>
              <CardTitle className="text-xl">{template.name}</CardTitle>
              <CardDescription>{template.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                <p className="font-medium mb-1">Tracks:</p>
                <p className="text-primary">
                  {template.primary_metric_name} ({template.primary_metric_unit})
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
