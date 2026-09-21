"""Email sending module."""

from __future__ import annotations

from prospector.models.lead import Lead


class EmailSender:
    """Send outreach emails to leads."""

    def send(self, lead: Lead, message: str) -> bool:
        """Send an email to the lead."""
        # TODO: implement email sending logic.
        print(f"E-mail enviado para {lead.email or 'sem-email'}")
        return bool(lead.email)
