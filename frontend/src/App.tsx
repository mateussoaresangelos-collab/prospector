import { useEffect, useMemo, useState } from 'react';

type Lead = {
  id?: number;
  search_id?: number;
  name: string;
  category: string;
  city: string;
  address: string;
  phone: string;
  email: string;
  website: string;
  instagram: string;
  score: number;
  status: string;
  favorite: boolean;
  notes: string;
  ai_message: string;
};

type HistoryItem = {
  id: number;
  city: string;
  category: string;
  lead_count: number;
  created_at?: string;
};

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export default function App() {
  const [city, setCity] = useState('São Paulo');
  const [category, setCategory] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('Todos');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  const loadLeads = async () => {
    try {
      const response = await fetch(`${API_URL}/leads`);
      if (!response.ok) throw new Error('Não foi possível carregar os leads.');
      const data = await response.json();
      setLeads(data);
      setError('');
    } catch (error) {
      console.error('Erro ao carregar leads:', error);
      setLeads([]);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/search/history`);
      if (!response.ok) throw new Error('Não foi possível buscar o histórico.');
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
      setHistory([]);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/categories`);
      if (!response.ok) throw new Error('Não foi possível buscar as categorias.');
      const data: string[] = await response.json();
      setCategories(data);
      setCategory((current) => current || data[0] || '');
    } catch (loadError) {
      console.error('Erro ao buscar categorias:', loadError);
      setError('Não foi possível carregar o catálogo de categorias.');
    }
  };

  useEffect(() => {
    void loadLeads();
    void loadHistory();
    void loadCategories();
  }, []);

  const handleSearch = async () => {
    if (!city.trim() || !category.trim()) {
      setError('Informe a cidade e a categoria para iniciar uma busca.');
      return;
    }

    setLoading(true);
    setError('');
    setNotice('');
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, category, force_refresh: false }),
      });

      if (!response.ok) {
        throw new Error('Falha ao buscar leads');
      }

      await loadLeads();
      await loadHistory();
      setNotice('Busca concluída. Os leads mais recentes estão prontos para prospecção.');
    } catch (error) {
      console.error(error);
      setError('A busca não pôde ser concluída. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const updateLeadStatus = async (lead: Lead) => {
    try {
      const response = await fetch(`${API_URL}/leads/${lead.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: lead.status, favorite: lead.favorite, notes: lead.notes }),
      });
      if (!response.ok) throw new Error('Falha ao atualizar lead');
      const updatedLead = await response.json();
      setLeads((current) => current.map((item) => item.id === updatedLead.id ? updatedLead : item));
      setSelectedLead((current) => current?.id === updatedLead.id ? updatedLead : current);
      setNotice('Lead atualizado com sucesso.');
    } catch (updateError) {
      console.error(updateError);
      setError('Não foi possível salvar esta alteração.');
    }
  };

  const filteredLeads = useMemo(() => leads.filter((lead) => {
    const matchesQuery = [lead.name, lead.city, lead.category, lead.email]
      .join(' ')
      .toLowerCase()
      .includes(query.toLowerCase());
    return matchesQuery && (statusFilter === 'Todos' || lead.status === statusFilter);
  }), [leads, query, statusFilter]);

  const totalWithWebsite = leads.filter((lead) => lead.website).length;
  const totalWithEmail = leads.filter((lead) => lead.email).length;
  const totalFavorites = leads.filter((lead) => lead.favorite).length;
  const averageScore = leads.length ? Math.round(leads.reduce((sum, lead) => sum + lead.score, 0) / leads.length) : 0;
  const formatDate = (value?: string) => value ? new Date(value).toLocaleDateString('pt-BR') : 'recente';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup"><div className="brand-mark">P</div><div><strong>Prospector</strong><span>Inteligência comercial</span></div></div>
        <div className="sidebar-section-label">Nova prospecção</div>
        <label>Cidade<input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Ex.: São Paulo" /></label>
        <label>Categoria<select value={category} onChange={(e) => setCategory(e.target.value)} disabled={!categories.length}><option value="">Selecione uma categoria</option>{categories.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        <button className="primary-button" onClick={handleSearch} disabled={loading}><span>{loading ? '◌' : '⌕'}</span>{loading ? 'Buscando oportunidades...' : 'Buscar oportunidades'}</button>
        <div className="sidebar-divider" />
        <div className="sidebar-section-label">Visão geral</div>
        <div className="side-stat"><span>Leads na base</span><strong>{leads.length}</strong></div>
        <div className="side-stat"><span>Favoritos</span><strong>{totalFavorites}</strong></div>

        <div className="history-panel">
          <div className="history-heading"><h3>Histórico recente</h3><span>{history.length}</span></div>
          <ul>
            {history.slice(0, 6).map((item) => (
              <li key={item.id}>
                <div><span>{item.city}</span><small>{formatDate(item.created_at)}</small></div>
                <strong>{item.category}</strong>
                <small>{item.lead_count} leads</small>
              </li>
            ))}
          </ul>
          {!history.length && <p className="empty-small">Suas buscas aparecerão aqui.</p>}
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <div className="eyebrow">CENTRAL DE PROSPECÇÃO <span className="live-dot" /> ONLINE</div>
            <h1>Encontre quem está pronto para conversar.</h1>
            <p>Organize sinais comerciais e transforme dados locais em próximas ações.</p>
          </div>
        </header>

        {error && <div className="alert error"><span>!</span>{error}<button onClick={() => setError('')}>×</button></div>}
        {notice && <div className="alert success"><span>✓</span>{notice}<button onClick={() => setNotice('')}>×</button></div>}

        <section className="kpis">
          <div className="kpi-card accent-cyan"><span>Leads encontrados</span><strong>{leads.length}</strong><small>na última pesquisa</small></div>
          <div className="kpi-card accent-green"><span>Com website</span><strong>{totalWithWebsite}</strong><small>{leads.length ? Math.round(totalWithWebsite / leads.length * 100) : 0}% da base</small></div>
          <div className="kpi-card accent-yellow"><span>Score médio</span><strong>{averageScore}<em>/100</em></strong><small>qualidade dos leads</small></div>
          <div className="kpi-card accent-violet"><span>Com email</span><strong>{totalWithEmail}</strong><small>prontos para contato</small></div>
        </section>

        <section className="table-panel">
          <div className="panel-heading"><div><span className="panel-kicker">PIPELINE ATIVO</span><h2>Seus leads</h2><p>{filteredLeads.length} resultados para trabalhar agora</p></div><div className="panel-actions"><label className="search-input"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar empresa, cidade..." /></label><select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}><option>Todos</option><option>Novo</option><option>Contatado</option><option>Em negociação</option><option>Cliente</option><option>Perdido</option></select><button className="refresh-button" onClick={() => { void loadLeads(); void loadHistory(); }} title="Atualizar dados">↻</button></div></div>
          <div className="table-scroll"><table>
            <thead>
              <tr>
                <th>Empresa</th>
                <th>Cidade</th>
                <th>Score</th>
                <th>Status</th>
                <th>Contato</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {filteredLeads.map((lead) => (
                <tr key={lead.id ?? lead.name}>
                  <td><button className="company-cell" onClick={() => setSelectedLead(lead)}><span className="company-avatar">{lead.name?.slice(0, 1).toUpperCase() || '?'}</span><span><strong>{lead.name || 'Empresa sem nome'}</strong><small>{lead.category}</small></span></button></td>
                  <td><span className="muted-cell">{lead.city || '—'}</span></td>
                  <td><span className={`score score-${lead.score >= 70 ? 'high' : lead.score >= 40 ? 'medium' : 'low'}`}>{lead.score}</span></td>
                  <td>
                    <select
                      className={`status status-${lead.status?.toLowerCase().replaceAll(' ', '-')}`}
                      value={lead.status}
                      onChange={(e) => { const updated = { ...lead, status: e.target.value }; setLeads((current) => current.map((item) => item.id === lead.id ? updated : item)); void updateLeadStatus(updated); }}
                    >
                      <option>Novo</option>
                      <option>Contatado</option>
                      <option>Em negociação</option>
                      <option>Cliente</option>
                      <option>Perdido</option>
                    </select>
                  </td>
                  <td><span className="contact-cell">{lead.email ? '✉ ' + lead.email : lead.phone ? '☎ ' + lead.phone : 'Sem contato'}</span></td>
                  <td className="row-actions">
                    <input
                      type="checkbox"
                      className="favorite-checkbox"
                      checked={lead.favorite}
                      onChange={(e) => { const updated = { ...lead, favorite: e.target.checked }; setLeads((current) => current.map((item) => item.id === lead.id ? updated : item)); void updateLeadStatus(updated); }}
                    />
                    <button className="details-button" onClick={() => setSelectedLead(lead)}>Ver detalhes</button>
                  </td>
                </tr>
              ))}
              {!filteredLeads.length && <tr><td colSpan={6}><div className="empty-state"><span>⌕</span><strong>Nenhum lead encontrado</strong><p>Ajuste os filtros ou faça uma nova busca.</p></div></td></tr>}
            </tbody>
          </table></div>
        </section>

        {selectedLead && <div className="drawer-backdrop" onClick={() => setSelectedLead(null)}><aside className="lead-drawer" onClick={(event) => event.stopPropagation()}><button className="close-button" onClick={() => setSelectedLead(null)}>×</button><div className="drawer-avatar">{selectedLead.name?.slice(0, 1).toUpperCase()}</div><span className="panel-kicker">DETALHE DO LEAD</span><h2>{selectedLead.name}</h2><p className="drawer-category">{selectedLead.category} · {selectedLead.city}</p><div className="drawer-score"><span>Lead score</span><strong>{selectedLead.score}<small>/100</small></strong></div><div className="drawer-details"><div><span>Email</span><strong>{selectedLead.email || 'Não encontrado'}</strong></div><div><span>Telefone</span><strong>{selectedLead.phone || 'Não encontrado'}</strong></div><div><span>Website</span><strong>{selectedLead.website || 'Não encontrado'}</strong></div><div><span>Endereço</span><strong>{selectedLead.address || 'Não informado'}</strong></div></div>{selectedLead.ai_message && <div className="ai-message"><span>✦ Mensagem sugerida</span><p>{selectedLead.ai_message}</p></div>}<button className="primary-button" onClick={() => setSelectedLead(null)}>Concluído</button></aside></div>}
      </main>
    </div>
  );
}
