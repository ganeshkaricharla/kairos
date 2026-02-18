import api from "./client";

export interface QuestionOption {
  value: string;
  label: string;
}

export interface Question {
  id: string;
  question: string;
  options: QuestionOption[];
}

export interface GoalTemplate {
  id: string;
  name: string;
  description: string;
  primary_metric_name: string;
  primary_metric_unit: string;
  icon: string;
  category: string;
  example_habits: string[];
  questionnaire: Question[];
}

export const goalTemplatesApi = {
  list: () => api.get<GoalTemplate[]>("/goal-templates").then((r) => r.data),
};
