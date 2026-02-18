"""
AI Prompts Package

This package contains all AI system prompts used by the coaching system.

New Prompt System (Integrated):
- initial_session: 3-phase goal creation conversation
- prompt_builder: Dynamic system prompt for regular coaching
- personalities: Coaching style fragments and mood detection
- review_session: Weekly and data-triggered review sessions
- proactive_checkin: Async background check-in triggers

Legacy Prompts (To be phased out):
- goal_analysis: Original goal setup (replaced by initial_session)
- progress_evaluation: Original progress review (replaced by review_session)

Utility Prompts:
- session_summary: Creates meeting-minutes style summaries
"""

# Make all prompt modules importable
from . import (
    initial_session,
    prompt_builder,
    personalities,
    review_session,
    proactive_checkin,
    session_summary,
    goal_analysis,
    progress_evaluation,
)

__all__ = [
    "initial_session",
    "prompt_builder",
    "personalities",
    "review_session",
    "proactive_checkin",
    "session_summary",
    "goal_analysis",
    "progress_evaluation",
]
