import { useNavigate } from "react-router-dom";
import { GoalForm } from "@/components/goals/GoalForm";
import { useCreateGoal } from "@/hooks/useGoals";

export function GoalSetupPage() {
  const navigate = useNavigate();
  const createGoal = useCreateGoal();

  async function handleGoalSubmit(data: {
    title: string;
    description: string;
    target_date?: string;
  }) {
    const goal = await createGoal.mutateAsync(data);
    // Goal creation auto-starts a coaching session — redirect to chat
    navigate(`/goals/${goal.id}/coach`);
  }

  return (
    <GoalForm
      onSubmit={handleGoalSubmit}
      loading={createGoal.isPending}
    />
  );
}
