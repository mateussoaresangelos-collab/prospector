import time
import tempfile
from pathlib import Path
from prospector.modules.google_maps import GoogleMapsSearcher
from prospector.modules.website_checker import WebsiteChecker
from prospector.modules.email_finder import EmailFinder
from prospector.modules.instagram import InstagramFinder
from prospector.modules.csv_exporter import CSVExporter
from prospector.modules.db import DBClient
from prospector.config import OUTPUT_DIR

categories = [
    'Restaurante', 'Pizzaria', 'Cafeteria', 'Farmácia', 'Dentista',
    'Academia', 'Loja de Roupas', 'Pet Shop', 'Advogado', 'Agência de Marketing',
    'Hotel', 'Escola', 'Banco', 'Clínica Médica', 'Bar',
    'Cabeleireiro', 'Oficina Mecânica', 'Floricultura', 'Lavanderia', 'Loja de Informática',
]

cities = [
    'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre',
    'Salvador', 'Brasília', 'Fortaleza', 'Manaus', 'Florianópolis',
]

pairings = [(cities[i % len(cities)], categories[i]) for i in range(len(categories))]

searcher = GoogleMapsSearcher(timeout=15)
checker = WebsiteChecker()
email_finder = EmailFinder(timeout=10)
instagram_finder = InstagramFinder()
csv_exporter = CSVExporter()

db_file = Path(tempfile.gettempdir()) / 'prospector_test_db.sqlite'
if db_file.exists():
    db_file.unlink()

db_client = DBClient(db_path=db_file)

print('TEST START')
print('Database path:', db_file)
print('Output file:', Path(OUTPUT_DIR) / 'prospector_test_leads.csv')

all_leads = []
for city, category in pairings:
    start = time.monotonic()
    leads = searcher.search(category=category, city=city, limit=5)
    duration = time.monotonic() - start
    names = [lead.name for lead in leads if lead.name]
    duplicates = [name for name in set(names) if names.count(name) > 1]
    print(f"{city} / {category}: {len(leads)} leads, duration={duration:.2f}s, duplicates={len(duplicates)}")
    all_leads.extend(leads)
    time.sleep(1)

sample_lead = None
for lead in all_leads:
    if lead.website:
        sample_lead = lead
        break
if sample_lead is None and all_leads:
    sample_lead = all_leads[0]

if sample_lead is None:
    print('No lead available for follow-up tests.')
else:
    print('\nSample lead for follow-up tests:')
    print('name=', sample_lead.name)
    print('city=', sample_lead.city)
    print('category=', sample_lead.category)
    print('website=', sample_lead.website)
    print('has_website=', checker.has_website(sample_lead))
    email_lead = email_finder.find_email(sample_lead)
    print('email found=', email_lead.email)
    print('instagram profile=', instagram_finder.find_profile(sample_lead))

    export_path = csv_exporter.export([sample_lead], Path(OUTPUT_DIR) / 'prospector_test_leads.csv')
    print('Exported sample lead CSV to', export_path)

    search_id = db_client.save_search(
        city=sample_lead.city,
        category=sample_lead.category,
        leads=[sample_lead],
        duration_seconds=3.14,
    )
    print('Saved sample search id', search_id)
    history = db_client.get_searches()
    print('Search history count after save', len(history))
    cached = db_client.get_last_search(sample_lead.city, sample_lead.category)
    print('Cached search found?', cached is not None)
    saved_leads = db_client.get_leads_for_search(search_id)
    print('Saved leads count for search id', search_id, len(saved_leads))
    db_client.delete_search(search_id)
    print('Deleted sample search id', search_id)

print('\nTesting invalid city handling...')
invalid_leads = searcher.search(category='Restaurante', city='CidadeInexistenteXYZ', limit=5)
print('Invalid city leads count', len(invalid_leads))

print('\nTesting SSL/timeout handling with EmailFinder...')
fast_email_finder = EmailFinder(timeout=1)
ssl_result = fast_email_finder._search_email_from_url('https://expired.badssl.com')
print('SSL invalid cert result', repr(ssl_result))
timeout_result = fast_email_finder._search_email_from_url('https://httpbin.org/delay/5')
print('Timeout result', repr(timeout_result))

print('TEST END')
