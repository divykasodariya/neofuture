import type { Transaction, Alert, GraphData, Stats } from '../types/schema';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiService = {
  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    const data = await response.json();
    const total_nodes = data.graph?.total_nodes || 1;
    const network_density = (data.graph?.total_edges || 0) / (total_nodes * total_nodes);
    return {
      total_transactions: data.graph?.total_edges || 0,
      total_alerts: data.alerts?.total_alerts || 0,
      active_alerts: data.alerts?.total_alerts || 0,
      network_density: network_density,
    };
  },

  async getAlerts(): Promise<Alert[]> {
    const response = await fetch(`${API_BASE_URL}/alerts`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    const data = await response.json();
    return data.alerts;
  },

  async getAlertDetail(id: string): Promise<Alert> {
    const response = await fetch(`${API_BASE_URL}/alerts/${id}`);
    if (!response.ok) throw new Error('Failed to fetch alert detail');
    return response.json();
  },

  async getGraph(accountId?: string): Promise<GraphData> {
    const url = accountId ? `${API_BASE_URL}/graph/${accountId}` : `${API_BASE_URL}/graph`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch graph data');
    return response.json();
  },

  async ingestTransaction(transaction: Partial<Transaction>): Promise<Transaction> {
    const response = await fetch(`${API_BASE_URL}/transaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transaction),
    });
    if (!response.ok) throw new Error('Failed to ingest transaction');
    return response.json();
  },
};
