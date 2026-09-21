"""Website validation module."""

from __future__ import annotations

from prospector.models.lead import Lead


class WebsiteChecker:
    """Check whether a lead has a website."""

    def has_website(self, lead: Lead) -> bool:
        """Return whether the lead has a website URL."""
        # TODO: implement website validation logic.
        return bool(lead.website and lead.website.strip())
