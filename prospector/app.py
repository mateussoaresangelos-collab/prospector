"""Streamlit-based visual interface for the Prospector AI workflow."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from prospector.config import LEADS_FILE
from prospector.models.lead import Lead
from prospector.modules.ai_generator import AIGenerator
from prospector.modules.csv_exporter import CSVExporter
from prospector.modules.db import DBClient
from prospector.modules.email_finder import EmailFinder
from prospector.modules.google_maps import GoogleMapsSearcher
from prospector.modules.instagram import InstagramFinder
from prospector.modules.website_checker import WebsiteChecker
from prospector.modules.categories import get_all_category_names

DB_CLIENT = DBClient()
LEAD_STATUSES = ["Novo", "Contatado", "Em negociação", "Cliente", "Perdido"]


def configure_page() -> None:
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="Prospector AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #06111f 0%, #0e1728 45%, #111827 100%);
            color: #f8fafc;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .hero-card, .metric-card, .panel-card {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(129, 140, 248, 0.22);
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(16px);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #8b5cf6;
        }
        .metric-label {
            font-size: 0.84rem;
            color: #94a3b8;
            margin-bottom: 0.35rem;
        }
        .section-title {
            color: #e2e8f0;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .stDataFrame {
            border-radius: 14px;
            overflow: hidden;
        }
        .stProgress .st-bo {
            background: linear-gradient(90deg, #8b5cf6, #22d3ee);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_leads(path: str | Path | None = None) -> list[Lead]:
    """Load leads from the exported CSV file when it exists."""
    target_path = Path(path or LEADS_FILE)
    if not target_path.exists() or target_path.stat().st_size == 0:
        return []

    frame = pd.read_csv(target_path)
    leads: list[Lead] = []
    for row in frame.to_dict(orient="records"):
        lead = Lead(
            name=_clean_value(row.get("name")),
            category=_clean_value(row.get("category")),
            city=_clean_value(row.get("city")),
            address=_clean_value(row.get("address")),
            phone=_clean_value(row.get("phone")),
            email=_clean_value(row.get("email")),
            website=_clean_value(row.get("website")),
            instagram=_clean_value(row.get("instagram")),
            linkedin=_clean_value(row.get("linkedin")),
            facebook=_clean_value(row.get("facebook")),
            whatsapp=_clean_value(row.get("whatsapp")),
            has_website=bool(row.get("has_website", False)),
            metadata={},
        )
        leads.append(lead)

    return leads


def load_recent_leads() -> list[Lead]:
    """Load the most recent saved search from SQLite if available."""
    searches = DB_CLIENT.get_searches()
    if not searches:
        return load_leads()

    latest = searches[0]
    st.session_state["last_search_id"] = latest["id"]
    st.session_state["last_search_city"] = latest["city"]
    st.session_state["last_search_category"] = latest["category"]
    st.session_state["last_search_duration"] = latest["duration_seconds"]
    return DB_CLIENT.get_leads_for_search(latest["id"])


def format_duration(seconds: float) -> str:
    """Format duration in seconds into a readable string."""
    if seconds is None:
        return "0s"
    minutes = int(seconds // 60)
    remaining = int(seconds % 60)
    if minutes:
        return f"{minutes}m {remaining}s"
    return f"{remaining}s"


def _clean_value(value: Any) -> str:
    """Normalize values coming from pandas or CSV rows."""
    if pd.isna(value):
        return ""
    return str(value)


def process_leads(city: str, category: str, force_refresh: bool = False) -> list[Lead]:
    """Run the existing prospecting pipeline for a city and category."""
    if not city.strip() or not category.strip():
        st.warning("Informe cidade e categoria para iniciar a busca.")
        return []

    if not force_refresh:
        cached = DB_CLIENT.get_last_search(city=city, category=category)
        if cached is not None:
            search, cached_leads = cached
            st.info(f"Carregando resultados existentes para {category} em {city}.")
            st.session_state["last_search_id"] = search["id"]
            st.session_state["last_search_city"] = search["city"]
            st.session_state["last_search_category"] = search["category"]
            st.session_state["last_search_duration"] = search["duration_seconds"]
            return cached_leads

    st.write("### Depuração de busca")
    st.write(f"cidade informada: {city!r}")
    st.write(f"categoria informada: {category!r}")

    searcher = GoogleMapsSearcher()
    checker = WebsiteChecker()
    instagram_finder = InstagramFinder()
    ai_generator = AIGenerator()
    email_finder = EmailFinder()

    progress_bar = st.progress(0)
    status_area = st.empty()
    status_container = st.empty()
    status_container.text("Encontrando empresas...")

    start_ts = time.monotonic()
    try:
        leads = searcher.search(category=category, city=city, limit=12)
        st.write(f"searcher.search() retornou {len(leads)} lead(s)")
    except Exception as exc:  # pragma: no cover - defensive UI guard
        st.error(f"Falha na busca inicial: {exc}")
        return []

    progress_bar.progress(0.2)
    status_container.text("Analisando websites...")

    processed_leads: list[Lead] = []
    total = max(len(leads), 1)

    for index, lead in enumerate(leads):
        try:
            lead.city = lead.city or city
            lead.category = lead.category or category

            status_area.text(f"Processando {lead.name or 'lead'}...")
            lead.has_website = checker.has_website(lead)

            if lead.has_website:
                lead = email_finder.find_email(lead)

            lead.instagram = instagram_finder.find_profile(lead)

            if lead.has_website and lead.email:
                message = ai_generator.generate_message(lead)
                lead.metadata["ai_message"] = message

            lead.status = _build_status(lead)
            lead.favorite = False
            lead.notes = lead.notes or ""
            lead.metadata["last_run"] = city
            processed_leads.append(lead)
        except Exception as exc:  # pragma: no cover - defensive UI guard
            lead.metadata["status"] = "Erro"
            lead.metadata["error"] = str(exc)
            processed_leads.append(lead)

        progress_bar.progress(0.2 + ((index + 1) / total) * 0.7)

    website_count = sum(1 for lead in processed_leads if lead.has_website)
    email_count = sum(1 for lead in processed_leads if lead.email)
    instagram_count = sum(1 for lead in processed_leads if lead.instagram)
    duration_seconds = time.monotonic() - start_ts

    st.write(
        "Leads após o pipeline:",
        f"total={len(processed_leads)}",
        f"website={website_count}",
        f"email={email_count}",
        f"instagram={instagram_count}",
    )

    DB_CLIENT.save_search(city=city, category=category, leads=processed_leads, duration_seconds=duration_seconds)
    exporter = CSVExporter()
    exporter.export(processed_leads, LEADS_FILE)
    progress_bar.progress(1.0)
    status_container.text("Finalizado")
    status_area.text(f"{len(processed_leads)} leads processados com sucesso.")
    st.success("Pipeline concluído com sucesso.")

    return processed_leads


def _build_status(lead: Lead) -> str:
    """Create a readable status label for the lead."""
    if lead.email:
        return "Com email"
    if lead.has_website:
        return "Com website"
    return "Sem email"


def show_dashboard(leads: list[Lead]) -> None:
    """Render a premium dashboard with KPI cards."""
    if not leads:
        st.info("Nenhum lead carregado ainda. Inicie uma busca para visualizar o painel.")
        return

    total = len(leads)
    with_website = sum(1 for lead in leads if lead.has_website)
    with_email = sum(1 for lead in leads if lead.email)
    with_instagram = sum(1 for lead in leads if lead.instagram)
    average_score = round(sum(lead.score for lead in leads) / total, 1) if total else 0.0
    city_label = st.session_state.get("last_search_city", "-")
    category_label = st.session_state.get("last_search_category", "-")
    duration_label = format_duration(st.session_state.get("last_search_duration", 0.0))

    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.markdown("### Dashboard executivo")
    st.markdown(
        "<p style='color:#94a3b8; margin-top:-0.5rem;'>Monitoramento em tempo real do pipeline comercial.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns(6)
    cards = [
        ("Total de leads", total, "#22d3ee"),
        ("Com website", with_website, "#34d399"),
        ("Com email", with_email, "#8b5cf6"),
        ("Com Instagram", with_instagram, "#38bdf8"),
        ("Lead Score médio", average_score, "#f59e0b"),
        ("Tempo da busca", duration_label, "#8b5cf6"),
    ]

    for col, (label, value, color) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value' style='color:{color};'>{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Pesquisa atual</div>", unsafe_allow_html=True)
    st.markdown(f"**Cidade:** {city_label}")
    st.markdown(f"**Categoria:** {category_label}")
    st.markdown(f"**Duração da busca:** {duration_label}")
    st.markdown("</div>", unsafe_allow_html=True)

    bucket_labels = ["0-20", "21-40", "41-60", "61-80", "81-100"]
    score_series = pd.Series([lead.score for lead in leads])
    score_hist = pd.cut(score_series, bins=[-1, 20, 40, 60, 80, 100], labels=bucket_labels, include_lowest=True)
    score_counts = score_hist.value_counts().reindex(bucket_labels).fillna(0).astype(int)

    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distribuição do Lead Score</div>", unsafe_allow_html=True)
    st.bar_chart(score_counts)
    st.markdown("</div>", unsafe_allow_html=True)

    percentage_data = pd.DataFrame(
        {
            "Com": [with_website, with_email, with_instagram],
            "Sem": [total - with_website, total - with_email, total - with_instagram],
        },
        index=["Website", "Email", "Instagram"],
    )
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Presença digital</div>", unsafe_allow_html=True)
    st.bar_chart(percentage_data)
    st.markdown("</div>", unsafe_allow_html=True)


def show_lead_table(leads: list[Lead]) -> None:
    """Render a professional lead table with filters and detail view."""
    if not leads:
        st.info("Nenhum lead disponível para gerenciar. Execute uma busca ou carregue uma pesquisa antiga.")
        return

    frame = pd.DataFrame([lead.to_dict() for lead in leads])
    frame["status"] = [lead.status or "Novo" for lead in leads]
    frame["favorite"] = ["★" if lead.favorite else "" for lead in leads]
    frame["lead_score"] = [lead.score for lead in leads]
    frame["has_website"] = ["Sim" if lead.has_website else "Não" for lead in leads]
    frame["has_email"] = ["Sim" if lead.email else "Não" for lead in leads]
    frame["has_instagram"] = ["Sim" if lead.instagram else "Não" for lead in leads]

    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Gerenciamento de Leads</div>", unsafe_allow_html=True)

    name_search = st.text_input("Buscar por nome", key="lead_search")
    city_filter = st.selectbox("Cidade", ["Todos"] + sorted({str(v) for v in frame["city"].dropna().unique()}), key="filter_city")
    category_filter = st.selectbox("Categoria", ["Todos"] + sorted({str(v) for v in frame["category"].dropna().unique()}), key="filter_category")
    website_filter = st.selectbox("Website", ["Todos", "Sim", "Não"], key="filter_website")
    email_filter = st.selectbox("Email", ["Todos", "Sim", "Não"], key="filter_email")
    instagram_filter = st.selectbox("Instagram", ["Todos", "Sim", "Não"], key="filter_instagram")
    status_filter = st.selectbox("Status", ["Todos"] + LEAD_STATUSES, key="filter_status")
    favorite_filter = st.selectbox("Favoritos", ["Todos", "Sim", "Não"], key="filter_favorite")

    filtered = frame.copy()
    if name_search:
        filtered = filtered[filtered["name"].astype(str).str.contains(name_search, case=False, na=False)]
    if city_filter != "Todos":
        filtered = filtered[filtered["city"] == city_filter]
    if category_filter != "Todos":
        filtered = filtered[filtered["category"] == category_filter]
    if website_filter != "Todos":
        filtered = filtered[filtered["has_website"] == website_filter]
    if email_filter != "Todos":
        filtered = filtered[filtered["has_email"] == email_filter]
    if instagram_filter != "Todos":
        filtered = filtered[filtered["has_instagram"] == instagram_filter]
    if status_filter != "Todos":
        filtered = filtered[filtered["status"] == status_filter]
    if favorite_filter != "Todos":
        if favorite_filter == "Sim":
            filtered = filtered[filtered["favorite"] == "★"]
        else:
            filtered = filtered[filtered["favorite"] == ""]

    sort_by = st.selectbox("Ordenar por", ["score", "name", "city", "category", "status"], index=0, key="sort_by")
    sort_order = st.selectbox("Ordem", ["Crescente", "Decrescente"], key="sort_order")
    filtered = filtered.sort_values(by=sort_by, ascending=sort_order == "Crescente", na_position="last")

    st.dataframe(filtered[ ["favorite", "name", "category", "city", "lead_score", "status", "phone", "email", "website", "instagram"] ], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    lead_names = [name for name in filtered["name"].tolist() if name]
    if not lead_names:
        return

    selected_name = st.selectbox("Selecionar lead", lead_names, key="selected_lead")
    selected_lead = next((lead for lead in leads if lead.name == selected_name), None)
    if not selected_lead:
        return

    st.markdown("")
    left, right = st.columns([2, 1])
    with left:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Detalhes do lead</div>", unsafe_allow_html=True)
        st.text_input("Empresa", value=selected_lead.name, key="detail_name", disabled=True)
        st.text_input("Categoria", value=selected_lead.category, key="detail_category", disabled=True)
        st.text_input("Cidade", value=selected_lead.city, key="detail_city", disabled=True)
        st.text_input("Telefone", value=selected_lead.phone, key="detail_phone", disabled=True)
        st.text_input("Website", value=selected_lead.website, key="detail_website", disabled=True)
        st.text_input("Email", value=selected_lead.email, key="detail_email", disabled=True)
        st.text_input("Instagram", value=selected_lead.instagram, key="detail_instagram", disabled=True)
        st.markdown(f"**Lead Score:** {selected_lead.score}")
        st.markdown(f"**Status atual:** {selected_lead.status}")
        st.markdown(f"**Favorito:** {'Sim' if selected_lead.favorite else 'Não'}")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Atualizar lead</div>", unsafe_allow_html=True)
        updated_status = st.selectbox("Status", LEAD_STATUSES, index=LEAD_STATUSES.index(selected_lead.status) if selected_lead.status in LEAD_STATUSES else 0, key="update_status")
        updated_favorite = st.checkbox("Favorito", value=selected_lead.favorite, key="update_favorite")
        updated_notes = st.text_area("Observações", value=selected_lead.notes or "", key="update_notes")
        if st.button("Salvar alterações", key="save_lead"):
            selected_lead.status = updated_status
            selected_lead.favorite = updated_favorite
            selected_lead.notes = updated_notes
            DB_CLIENT.update_lead(selected_lead)
            st.success("Lead salvo com sucesso.")

        if selected_lead.id is not None and st.button("Excluir lead", key="delete_lead"):
            DB_CLIENT.delete_lead(selected_lead.id)
            st.success("Lead removido do banco de dados.")
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def show_search_history() -> None:
    """Render a history view for saved searches."""
    searches = DB_CLIENT.get_searches()
    if not searches:
        st.info("Nenhuma pesquisa salva ainda. Execute uma busca para gerar histórico.")
        return

    history = pd.DataFrame(searches)
    history["duration"] = history["duration_seconds"].apply(format_duration)
    history = history[["id", "city", "category", "created_at", "lead_count", "website_count", "email_count", "instagram_count", "average_score", "duration"]]
    history = history.rename(columns={
        "id": "ID",
        "city": "Cidade",
        "category": "Categoria",
        "created_at": "Data",
        "lead_count": "Leads",
        "website_count": "Websites",
        "email_count": "Emails",
        "instagram_count": "Instagram",
        "average_score": "Score médio",
        "duration": "Duração",
    })

    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Histórico de pesquisas</div>", unsafe_allow_html=True)
    st.dataframe(history, use_container_width=True)

    selected_id = st.selectbox(
        "Carregar pesquisa",
        [row["id"] for row in searches],
        format_func=lambda value: f"{value} - {next(item['city'] for item in searches if item['id'] == value)} / {next(item['category'] for item in searches if item['id'] == value)}",
        key="history_select",
    )
    if st.button("Carregar pesquisa selecionada", key="load_history"):
        selected_search = DB_CLIENT.get_search_by_id(selected_id)
        if selected_search:
            saved_leads = DB_CLIENT.get_leads_for_search(selected_id)
            st.session_state["leads"] = saved_leads
            st.session_state["city"] = selected_search["city"]
            st.session_state["category"] = selected_search["category"]
            st.session_state["last_search_id"] = selected_search["id"]
            st.session_state["last_search_duration"] = selected_search["duration_seconds"]
            st.success("Pesquisa carregada com sucesso.")
            st.experimental_rerun()
        else:
            st.error("Não foi possível carregar a pesquisa selecionada.")

    if st.button("Excluir pesquisa selecionada", key="delete_history"):
        DB_CLIENT.delete_search(selected_id)
        st.success("Pesquisa excluída com sucesso.")
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Render the visual application shell."""
    configure_page()

    st.markdown(
        """
        <div class='hero-card'>
            <h1 style='margin-bottom:0.25rem;'>PROSPECTOR AI</h1>
            <p style='color:#94a3b8; margin-top:0;'>Inteligência artificial para encontrar oportunidades comerciais com precisão.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "city" not in st.session_state:
        st.session_state["city"] = ""
    if "category" not in st.session_state:
        st.session_state["category"] = ""

    with st.sidebar:
        st.header("Operação")
        st.caption("Defina a cidade e a categoria para disparar o fluxo completa.")

        city = st.text_input("Cidade", value=st.session_state["city"], key="city")
        categories = get_all_category_names()
        # determine initial index based on previous session value when possible
        try:
            initial_index = categories.index(st.session_state.get("category", ""))
        except ValueError:
            initial_index = 0
        category = st.selectbox("Categoria", categories, index=initial_index, key="category")

        if st.button("Buscar leads", use_container_width=True):
            st.session_state["leads"] = process_leads(city, category, force_refresh=False)

        if st.button("Atualizar dados", use_container_width=True):
            st.session_state["leads"] = process_leads(city, category, force_refresh=True)

        if st.button("Exportar leads", use_container_width=True):
            leads = st.session_state.get("leads", [])
            if leads:
                exporter = CSVExporter()
                output_path = exporter.export(leads, LEADS_FILE)
                st.success(f"Leads exportados em {output_path}")
            else:
                st.info("Nenhum lead disponível para exportar.")

        st.markdown("---")
        st.caption("Fluxo: busca de leads → verificação de website → descoberta de email → Instagram → IA → exportação")

    if "leads" not in st.session_state:
        st.session_state["leads"] = load_leads()

    leads = st.session_state.get("leads", [])
    show_dashboard(leads)
    show_lead_table(leads)


if __name__ == "__main__":
    main()
