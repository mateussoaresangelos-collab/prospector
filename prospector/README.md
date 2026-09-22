# Módulos Prospector

Este diretório contém os módulos de negócio compartilhados pela API FastAPI:

- `modules/google_maps.py`: descoberta via Nominatim e Overpass/OpenStreetMap.
- `modules/email_finder.py`: busca de emails públicos em websites.
- `modules/website_checker.py`: verificação básica de presença de website.
- `modules/db.py`: persistência SQLite de pesquisas e leads.
- `modules/csv_exporter.py`: exportação dos leads para CSV.
- `models/lead.py`: modelo interno de lead.
- `config.py`: caminhos locais de dados.

A interface principal do projeto é o conjunto React + FastAPI documentado no `README.md` da raiz. A antiga interface Streamlit foi arquivada em `legacy/streamlit/`.
