export interface Transaction {
  id: string;
  timestamp: string;
  amount: number;
  currency: string;
  account_id: string;
  merchant_id: string;
  device_id: string;
  location: string;
  is_fraud: boolean;
}

export interface Alert {
  id: string;
  timestamp: string;
  rule_id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  involved_accounts: string[];
  status: 'pending' | 'investigating' | 'resolved' | 'dismissed';
}

export interface GraphNode {
  id: string;
  type: 'account' | 'merchant' | 'device';
  label: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  amount?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Stats {
  total_transactions: number;
  total_alerts: number;
  active_alerts: number;
  network_density: number;
}
