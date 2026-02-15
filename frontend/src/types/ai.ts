export interface ChangeProposal {
  type: string;
  description: string;
  details: Record<string, unknown>;
}

export interface CoachingReply {
  message: string;
  proposed_changes: ChangeProposal[];
}
