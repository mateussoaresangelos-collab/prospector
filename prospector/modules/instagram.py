"""Instagram profile search module."""

from __future__ import annotations

from prospector.models.lead import Lead


class InstagramFinder:
    """Find Instagram profiles for a lead."""

    def find_profile(self, lead: Lead) -> str:
        """Return the Instagram profile for the given lead."""
        # TODO: implement Instagram profile search logic.
        return lead.instagram or ""
