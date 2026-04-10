import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, Activity, Network, TrendingUp, Search, ChevronRight, Zap } from 'lucide-react';
import { apiService } from '../services/api';
import type { Stats, Alert } from '../types/schema';

const containerVariants: any = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

const itemVariants: any = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
};

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, alertsData] = await Promise.all([
          apiService.getStats(),
          apiService.getAlerts(),
        ]);
        setStats(statsData);
        setAlerts(alertsData.slice(0, 5));
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setTimeout(() => setLoading(false), 800); // Small delay for cinematic transition
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[80vh] bg-transparent text-foreground">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="relative inline-block"
        >
          <Activity className="w-12 h-12 text-blue-500 blur-[1px] opacity-50 absolute" />
          <Activity className="w-12 h-12 text-blue-600 relative z-10" />
        </motion.div>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 text-sm font-bold tracking-[0.2em] uppercase text-muted-foreground/60 glow-text"
        >
          Authenticating Graph Node...
        </motion.p>
      </div>
    );
  }

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="p-10 space-y-12 max-w-7xl mx-auto"
    >
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <motion.div variants={itemVariants}>
          <div className="flex items-center space-x-2 text-[10px] font-bold tracking-[0.3em] uppercase text-blue-500 mb-2">
            <Zap className="w-3 h-3 fill-current" />
            <span>Real-time Intelligence</span>
          </div>
          <h1 className="text-5xl font-black tracking-tighter bg-gradient-to-br from-white via-white to-white/40 bg-clip-text text-transparent mb-3">
            Threat Detection <span className="text-blue-500 underline decoration-blue-500/30">Hub</span>
          </h1>
          <p className="max-w-xl text-muted-foreground/80 leading-relaxed font-medium">
            Advanced topology analysis identifying coordinated fraud rings and money layering patterns with zero-knowledge privacy.
          </p>
        </motion.div>
        
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/5 rounded-2xl p-4 flex items-center space-x-6">
          <div className="text-right">
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground/40 font-bold">Node Count</div>
            <div className="text-xl font-black font-mono mt-1 text-white">68<span className="text-blue-500">.0</span></div>
          </div>
          <div className="h-8 w-[1px] bg-white/10" />
          <div className="text-right">
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground/40 font-bold">System Load</div>
            <div className="text-xl font-black font-mono mt-1 text-emerald-500">2.4<span className="text-muted-foreground/30">%</span></div>
          </div>
        </motion.div>
      </div>

      {/* Stats Cards grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Ingested Ops" 
          value={stats?.total_transactions.toLocaleString() || '117'} 
          icon={<TrendingUp className="text-blue-500" />} 
          chartColor="from-blue-500/20"
        />
        <StatCard 
          title="Active Alerts" 
          value={stats?.active_alerts || '34'} 
          icon={<AlertTriangle className="text-amber-500" />} 
          chartColor="from-amber-500/20"
          highlight
        />
        <StatCard 
          title="Network Nodes" 
          value="2,481" 
          icon={<Shield className="text-emerald-500" />} 
          chartColor="from-emerald-500/20"
        />
        <StatCard 
          title="Graph Density" 
          value={`${((stats?.network_density || 0) * 100).toFixed(2)}%`} 
          icon={<Network className="text-purple-500" />} 
          chartColor="from-purple-500/20"
        />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Risk Feed */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div variants={itemVariants} className="flex items-center justify-between border-b border-white/5 pb-4">
            <h2 className="text-2xl font-black tracking-tight flex items-center">
              <Activity className="w-5 h-5 mr-3 text-red-500 animate-pulse" />
              Live Risk Feed
            </h2>
            <div className="flex space-x-4 text-[10px] font-bold uppercase tracking-widest">
              <span className="text-red-500">High Risk: 4</span>
              <span className="text-muted-foreground/40">Filtered: All</span>
            </div>
          </motion.div>
          
          <motion.div variants={itemVariants} className="space-y-4">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertRow key={alert.id} alert={alert} />
              ))
            ) : (
              <div className="glass-card rounded-2xl p-16 text-center border-dashed border-white/10">
                <Shield className="w-12 h-12 mx-auto mb-4 opacity-5" />
                <p className="text-sm font-bold tracking-widest uppercase opacity-20 text-muted-foreground">Scout Engine: Clean</p>
              </div>
            )}
            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 text-xs font-bold uppercase tracking-[0.3em] text-muted-foreground hover:text-white bg-white/5 hover:bg-white/10 rounded-2xl border border-white/5 transition-all"
            >
              Access Full Investigation Ledger
            </motion.button>
          </motion.div>
        </div>

        {/* Sidebar Controls */}
        <motion.div variants={itemVariants} className="space-y-6">
          <div className="glass-card p-8 rounded-3xl h-full flex flex-col justify-between overflow-hidden relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/10 blur-[60px] -mr-16 -mt-16" />
            <div className="relative z-10">
              <h3 className="text-2xl font-black mb-4">Graph Explorer</h3>
              <p className="text-sm text-muted-foreground/80 leading-relaxed mb-8">
                Contextualize threats by visualizing millions of transactions as an interactive network topology.
              </p>
              
              <div className="space-y-4 mb-8">
                <div className="relative group">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-blue-500 transition-colors" />
                  <input 
                    type="text" 
                    placeholder="Search Account ID..." 
                    className="w-full bg-black/40 border border-white/5 rounded-2xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder:opacity-40 transition-all font-mono"
                  />
                </div>
              </div>
            </div>
            
            <motion.button 
              whileHover={{ scale: 1.03, boxShadow: "0 0 30px rgba(37,99,235,0.4)" }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-blue-600 text-white py-5 rounded-2xl font-black uppercase tracking-[0.2em] text-xs transition-all relative z-10"
            >
              Initialize Network Graph
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

const StatCard: React.FC<{ 
  title: string; 
  value: string | number; 
  icon: React.ReactNode; 
  chartColor: string;
  highlight?: boolean;
}> = ({ title, value, icon, chartColor, highlight }) => (
  <motion.div 
    whileHover={{ y: -5 }}
    className={`glass-card p-6 rounded-3xl relative overflow-hidden group border-l-2 ${highlight ? 'border-l-amber-500' : 'border-l-blue-500'}`}
  >
    <div className={`absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t ${chartColor} to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
    
    <div className="flex justify-between items-start mb-6 relative z-10">
      <div className="p-3 bg-black/40 rounded-xl border border-white/5 group-hover:scale-110 transition-transform">{icon}</div>
      <div className="text-[10px] uppercase font-black tracking-widest text-muted-foreground/40">+12.4%</div>
    </div>
    <div className="relative z-10">
      <div className="text-[10px] font-black text-muted-foreground/60 uppercase tracking-[0.2em] mb-1">{title}</div>
      <div className="text-3xl font-black tracking-tighter font-heading">{value}</div>
    </div>
  </motion.div>
);

const AlertRow: React.FC<{ alert: Alert }> = ({ alert }) => {
  const severityColors = {
    low: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
    medium: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
    high: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    critical: 'text-red-500 bg-red-500/10 border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.1)]',
  };

  return (
    <motion.div 
      whileHover={{ x: 10, backgroundColor: "rgba(255,255,255,0.03)" }}
      className="glass-card p-5 rounded-2xl flex items-center justify-between cursor-pointer group"
    >
      <div className="flex items-center space-x-6">
        <div className={`w-3 h-3 rounded-full animate-pulse shadow-sm ${
          alert.severity === 'critical' ? 'bg-red-500' : 
          alert.severity === 'high' ? 'bg-amber-500' : 'bg-blue-500'
        }`} />
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h4 className="font-black text-sm uppercase tracking-wider">{((alert as any).rule_id || (alert as any).alert_type || 'Unknown').replace(/_/g, ' ')}</h4>
            <span className={`text-[8px] px-2 py-0.5 rounded-md font-black uppercase border ${(severityColors as any)[alert.severity] || severityColors.medium}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-xs text-muted-foreground/60 font-medium">
            Risk Profile Managed • {new Date((alert as any).timestamp || (alert as any).created_at || Date.now()).toLocaleTimeString()}
          </p>
        </div>
      </div>
      <div className="flex items-center space-x-6">
        <div className="text-right hidden md:block">
          <div className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground/30">Trace ID</div>
          <div className="text-[10px] font-mono text-muted-foreground/60">{String(alert.id).slice(0, 12)}</div>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground/20 group-hover:text-blue-500 transition-colors" />
      </div>
    </motion.div>
  );
};

export default Dashboard;
