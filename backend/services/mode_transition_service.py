"""
Mode Transition Service - Soft guardrails for workflow navigation

Transition Types:
- forward_ready: Moving forward with prerequisites met
- forward_skip: Moving forward without prerequisites (allowed but noted)
- backward_revision: Going back to revise earlier work
- lateral: Staying in same phase but different focus
- same: Already in target mode

Philosophy: The Foreman is an advisor, not a gatekeeper.
"""

import asyncio
from typing import Literal

TransitionType = Literal[
    "forward_ready",
    "forward_skip",
    "backward_revision",
    "lateral",
    "same"
]

# Mode ordering for forward/backward detection
MODE_ORDER = ["ARCHITECT", "VOICE_CALIBRATION", "DIRECTOR", "EDITOR"]

# Prerequisites for each mode
MODE_PREREQUISITES = {
    "ARCHITECT": [],  # Always available
    "VOICE_CALIBRATION": [
        {"name": "story_bible_started", "check": "story_bible_has_protagonist"},
        {"name": "beat_sheet_exists", "check": "beat_sheet_has_beats"},
    ],
    "DIRECTOR": [
        {"name": "voice_calibrated", "check": "voice_bundle_exists"},
        {"name": "story_bible_complete", "check": "story_bible_complete"},
    ],
    "EDITOR": [
        {"name": "has_draft_content", "check": "manuscript_has_scenes"},
    ],
}

# Canned context templates - the WHAT to say
TRANSITION_TEMPLATES = {
    "same": {
        "context": "Writer clicked on mode they're already in.",
        "guidance": "Acknowledge and offer to continue or explore options.",
        "tone": "friendly, brief"
    },
    "forward_ready": {
        "context": "Writer is ready to advance. Prerequisites met.",
        "guidance": "Celebrate progress, briefly explain what this mode offers.",
        "tone": "encouraging, forward-looking"
    },
    "forward_skip": {
        "context": "Writer wants to skip ahead. Missing: {missing}",
        "guidance": "Acknowledge intent, explain what's missing without blocking. Offer two paths: quick setup OR proceed anyway.",
        "tone": "supportive, practical"
    },
    "backward_revision": {
        "context": "Writer wants to revisit earlier work from {current} back to {target}.",
        "guidance": "Validate this is common and smart. Ask what aspect needs revision.",
        "tone": "understanding, curious"
    },
}


async def get_mode_prerequisites(target_mode: str) -> list[dict]:
    """Get prerequisites with completion status."""
    prereqs = MODE_PREREQUISITES.get(target_mode.upper(), [])
    results = []

    for prereq in prereqs:
        completed = await check_prerequisite(prereq["check"])
        results.append({
            "name": prereq["name"],
            "completed": completed
        })

    return results


async def check_prerequisite(check_name: str) -> bool:
    """Check if a specific prerequisite is met."""
    try:
        # Import services inside function to avoid circular imports
        from backend.services.story_bible_service import story_bible_service
        from backend.services.voice_calibration_service import voice_calibration_service

        checks = {
            "story_bible_has_protagonist": lambda: story_bible_service.has_protagonist(),
            "beat_sheet_has_beats": lambda: story_bible_service.beat_count() > 0,
            "voice_bundle_exists": lambda: voice_calibration_service.has_voice_bundle(),
            "story_bible_complete": lambda: story_bible_service.is_complete(),
            "manuscript_has_scenes": lambda: True,  # TODO: Check manuscript service
        }

        checker = checks.get(check_name)
        if checker:
            result = checker()
            if asyncio.iscoroutine(result):
                return await result
            return result
        return False
    except Exception as e:
        print(f"Warning: Prerequisite check '{check_name}' failed: {e}")
        return False


def classify_transition(current: str, target: str, missing: list) -> TransitionType:
    """Classify the type of mode transition."""
    current = current.upper()
    target = target.upper()

    if current == target:
        return "same"

    current_idx = MODE_ORDER.index(current) if current in MODE_ORDER else 0
    target_idx = MODE_ORDER.index(target) if target in MODE_ORDER else 0

    if target_idx > current_idx:
        # Moving forward
        if not missing:
            return "forward_ready"
        else:
            return "forward_skip"
    else:
        # Moving backward
        return "backward_revision"


async def generate_transition_response(
    current_mode: str,
    target_mode: str,
    transition_type: TransitionType,
    missing_prerequisites: list
) -> str:
    """Generate a contextual, conversational response using hybrid approach."""

    template = TRANSITION_TEMPLATES.get(transition_type, TRANSITION_TEMPLATES["same"])

    # Format the context with any placeholders
    context = template["context"].format(
        missing=", ".join([p["name"] for p in missing_prerequisites]) if missing_prerequisites else "none",
        current=current_mode,
        target=target_mode
    )

    # Build the prompt for the LLM
    system_prompt = f"""You are the Foreman, a creative writing partner.

The writer just clicked the {target_mode} mode button.
Current mode: {current_mode}
Transition type: {transition_type}

Context: {context}

Your guidance: {template["guidance"]}
Tone: {template["tone"]}

Respond in 2-3 sentences max. Be conversational, not robotic.
Do NOT use phrases like "I understand" or "Great choice".
"""

    try:
        # Use local model for quick response
        from backend.services.llm_service import llm_service

        response = await llm_service.generate(
            provider="ollama",
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"I want to switch to {target_mode} mode."}
            ],
            temperature=0.7,
            max_tokens=150
        )

        return response.content
    except Exception as e:
        # Fallback to canned response if LLM fails
        print(f"Warning: LLM response generation failed: {e}")
        return _get_fallback_response(transition_type, target_mode, missing_prerequisites)


def _get_fallback_response(
    transition_type: TransitionType,
    target_mode: str,
    missing_prerequisites: list
) -> str:
    """Fallback responses when LLM is unavailable."""
    fallbacks = {
        "same": f"You're already in {target_mode} mode. What would you like to work on?",
        "forward_ready": f"Moving to {target_mode} mode. Let's get started!",
        "forward_skip": f"Switching to {target_mode} mode. Note: some prerequisites aren't complete yet ({', '.join([p['name'] for p in missing_prerequisites])}), but we can proceed.",
        "backward_revision": f"Going back to {target_mode} mode. What would you like to revise?",
    }
    return fallbacks.get(transition_type, f"Switching to {target_mode} mode.")


class ModeTransitionService:
    """Service for handling mode transitions with soft guardrails."""

    async def request_transition(self, current_mode: str, target_mode: str) -> dict:
        """
        Process a mode transition request.

        Returns:
            dict with keys: allowed, new_mode, foreman_message, missing_prerequisites
        """
        target = target_mode.upper()
        current = current_mode.upper()

        # Get prerequisite status
        prereqs = await get_mode_prerequisites(target)
        missing = [p for p in prereqs if not p["completed"]]

        # Determine transition type
        transition_type = classify_transition(current, target, missing)

        # Generate contextual response
        foreman_message = await generate_transition_response(
            current_mode=current,
            target_mode=target,
            transition_type=transition_type,
            missing_prerequisites=missing
        )

        # Decide if mode actually changes
        # Note: forward_skip now ALLOWS the transition (soft guardrails)
        if transition_type in ["forward_ready", "forward_skip", "backward_revision"]:
            allowed = True
            new_mode = target
        else:
            # Only "same" doesn't change mode
            allowed = False
            new_mode = None

        return {
            "allowed": allowed,
            "new_mode": new_mode,
            "foreman_message": foreman_message,
            "missing_prerequisites": [p["name"] for p in missing],
            "transition_type": transition_type
        }


# Singleton instance
mode_transition_service = ModeTransitionService()
