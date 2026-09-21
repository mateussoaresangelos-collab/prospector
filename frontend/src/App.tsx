import { useEffect, useState } from 'react';

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

const API_URL = 'http://localhost:8000';

export default function App() {
  const [city, setCity] = useState('São Paulo');
  const [category, setCategory] = useState('advogados');
  const [loading, setLoading] = useState(false);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  const loadLeads = async () => {
    try {
      const response = await fetch(`${API_URL}/leads`);
      const data = await response.json();
      setLeads(data);
    } catch (error) {
      console.error('Erro ao carregar leads:', error);
      setLeads([]);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/search/history`);
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
      setHistory([]);
    }
  };

  useEffect(() => {
    void loadLeads();
    void loadHistory();
  }, []);

  const handleSearch = async () => {
    setLoading(true);
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
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateLeadStatus = async (lead: Lead) => {
    await fetch(`${API_URL}/leads/${lead.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: lead.status,
        favorite: lead.favorite,
        notes: lead.notes,
      }),
    });
    await loadLeads();
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">PROSPECTOR AI</div>
        <label>
          Cidade
          <input value={city} onChange={(e) => setCity(e.target.value)} />
        </label>
        <label>
          Categoria
          <input value={category} onChange={(e) => setCategory(e.target.value)} />
        </label>
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Buscando...' : 'Buscar leads'}
        </button>

        <div className="history-panel">
          <h3>Histórico</h3>
          <ul>
            {history.slice(0, 6).map((item) => (
              <li key={item.id}>
                <span>{item.city}</span>
                <strong>{item.category}</strong>
                <small>{item.lead_count} leads</small>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <h1>Dashboard executivo</h1>
            <p>Oportunidades comerciais em tempo real.</p>
          </div>
          <div className="kpis">
            <div className="kpi-card">
              <span>Total</span>
              <strong>{leads.length}</strong>
            </div>
            <div className="kpi-card">
              <span>Website</span>
              <strong>{leads.filter((lead) => lead.website).length}</strong>
            </div>
            <div className="kpi-card">
              <span>Email</span>
              <strong>{leads.filter((lead) => lead.email).length}</strong>
            </div>
          </div>
        </header>

        <section className="table-panel">
          <h2>Leads</h2>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Cidade</th>
                <th>Categoria</th>
                <th>Score</th>
                <th>Status</th>
                <th>Email</th>
                <th>Favorito</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id ?? lead.name}>
                  <td>{lead.name}</td>
                  <td>{lead.city}</td>
                  <td>{lead.category}</td>
                  <td>{lead.score}</td>
                  <td>
                    <select
                      value={lead.status}
                      onChange={(e) => {
                        lead.status = e.target.value;
                        void updateLeadStatus(lead);
                      }}
                    >
                      <option>Novo</option>
                      <option>Contatado</option>
                      <option>Em negociação</option>
                      <option>Cliente</option>
                      <option>Perdido</option>
                    </select>
                  </td>
                  <td>{lead.email || '—'}</td>
                  <td>
                    <input
                      type="checkbox"
                      checked={lead.favorite}
                      onChange={(e) => {
                        lead.favorite = e.target.checked;
                        void updateLeadStatus(lead);
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}
