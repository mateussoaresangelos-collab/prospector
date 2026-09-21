# Prospector

Prospector é uma estrutura base para uma ferramenta profissional de prospecção de clientes para venda de sites.

## Estrutura do projeto

- main.py: ponto de entrada do fluxo principal.
- config.py: configurações e caminhos do projeto.
- models/lead.py: modelo Lead usando dataclass.
- modules/: módulos especializados por responsabilidade.
  - google_maps.py: busca de leads em fontes de localização.
  - instagram.py: busca de perfis do Instagram.
  - website_checker.py: verificação de presença de site.
  - csv_exporter.py: exportação dos leads para CSV.
  - ai_generator.py: geração de mensagens de prospecção.
  - email_sender.py: envio de e-mails.
- data/: arquivos de dados e saída.

## Princípios aplicados

- Orientação a objetos.
- Type hints.
- Docstrings.
- PEP 8.
- Arquitetura preparada para crescimento.

## Próximos passos

- Implementar a lógica real de busca de leads.
- Integrar APIs ou scraping.
- Adicionar validações e logs.
- Melhorar o fluxo de exportação e envio.
