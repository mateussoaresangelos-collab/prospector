"""Entry point for the prospector application."""

from prospector.config import LEADS_FILE
from prospector.modules.ai_generator import AIGenerator
from prospector.modules.csv_exporter import CSVExporter
from prospector.modules.email_sender import EmailSender
from prospector.modules.email_finder import EmailFinder
from prospector.modules.google_maps import GoogleMapsSearcher
from prospector.modules.instagram import InstagramFinder
from prospector.modules.website_checker import WebsiteChecker


def main() -> None:
    """Run the prospecting workflow."""
    print("=" * 40)
    print("      PROSPECTOR AI")
    print("=" * 40)

    city = input("Cidade: ").strip()
    category = input("Categoria: ").strip()

    searcher = GoogleMapsSearcher()
    checker = WebsiteChecker()
    instagram_finder = InstagramFinder()
    ai_generator = AIGenerator()
    exporter = CSVExporter()
    email_sender = EmailSender()
    email_finder = EmailFinder()

    leads = searcher.search(category=category, city=city)

    for lead in leads:
        lead.city = lead.city or city
        lead.category = lead.category or category

        lead.has_website = checker.has_website(lead)

        if lead.has_website:
            lead = email_finder.find_email(lead)

        lead.instagram = instagram_finder.find_profile(lead)

        if lead.has_website and lead.email:
            message = ai_generator.generate_message(lead)
            email_sender.send(
                lead=lead,
                message=message,
            )

    exporter.export(leads, LEADS_FILE)
    print(f"\n{len(leads)} leads processados.")


if __name__ == "__main__":
    main()
