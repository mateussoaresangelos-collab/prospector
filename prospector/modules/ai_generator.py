"""AI-based message generation module."""

from __future__ import annotations

from prospector.models.lead import Lead


class AIGenerator:
    """Generate outreach messages for leads."""

    def generate_message(self, lead: Lead) -> str:
        """Create a personalized message for the lead."""
        # TODO: implement AI message generation logic.
        return f"Olá {lead.name or 'cliente'}, tudo bem?"
