import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Dashboard from './pages/Dashboard';
import GraphExplorer from './pages/GraphExplorer';
import { Shield, Network, LayoutDashboard, History, Settings as SettingsIcon } from 'lucide-react';

type Page = 'dashboard' | 'graph' | 'transactions' | 'settings';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 grid-bg z-0" />
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px] animate-glow z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 rounded-full blur-[120px] animate-glow z-0" />

      {/* Navbar */}
      <nav className="border-b border-white/5 bg-card/30 backdrop-blur-2xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-3 group cursor-pointer" 
            onClick={() => setCurrentPage('dashboard')}
          >
            <div className="p-2 bg-blue-600 rounded-xl group-hover:scale-110 transition-transform shadow-[0_0_20px_rgba(37,99,235,0.4)]">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tighter glow-text">zkTransact</span>
          </motion.div>

          <div className="flex items-center space-x-1 p-1 bg-white/5 rounded-xl border border-white/5">
            <NavButton 
              active={currentPage === 'dashboard'} 
              onClick={() => setCurrentPage('dashboard')}
              icon={<LayoutDashboard className="w-4 h-4" />}
              label="Dashboard"
            />
            <NavButton 
              active={currentPage === 'graph'} 
              onClick={() => setCurrentPage('graph')}
              icon={<Network className="w-4 h-4" />}
              label="Explorer"
            />
            <NavButton 
              active={currentPage === 'transactions'} 
              onClick={() => setCurrentPage('transactions')}
              icon={<History className="w-4 h-4" />}
              label="Activity"
            />
          </div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <div className="h-4 w-[1px] bg-white/10 mx-2" />
            <button className="p-2 hover:bg-white/5 rounded-xl transition-colors text-muted-foreground hover:text-foreground">
              <SettingsIcon className="w-5 h-5" />
            </button>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 border border-white/10 shadow-lg cursor-pointer hover:scale-105 transition-transform" />
          </motion.div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 relative z-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 10, filter: 'blur(10px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -10, filter: 'blur(10px)' }}
            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            className="h-full"
          >
            {currentPage === 'dashboard' && <Dashboard />}
            {currentPage === 'graph' && <GraphExplorer />}
            {currentPage === 'transactions' && (
              <div className="p-20 text-center space-y-4">
                <History className="w-16 h-16 mx-auto opacity-10" />
                <h2 className="text-2xl font-bold text-muted-foreground">Historical Ledger</h2>
                <p className="max-w-md mx-auto text-sm text-muted-foreground/60">Comprehensive audit trail of all privacy-preserved transaction events coming soon.</p>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </main>
      
      {/* Footer */}
      <footer className="py-8 border-t border-white/5 bg-black/20 text-center relative z-10">
        <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground/40 font-bold mb-1">Authenticated Session</p>
        <p className="text-xs text-muted-foreground/30">
          &copy; 2026 zkTransact. Zero-Knowledge Compliance Engine.
        </p>
      </footer>
    </div>
  );
}

const NavButton: React.FC<{ active: boolean; onClick: () => void; icon: React.ReactNode; label: string }> = ({ 
  active, onClick, icon, label 
}) => (
  <button 
    onClick={onClick}
    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all relative ${
      active 
        ? 'text-white' 
        : 'text-muted-foreground hover:text-foreground'
    }`}
  >
    {active && (
      <motion.div 
        layoutId="nav-bg"
        className="absolute inset-0 bg-blue-600 shadow-[0_0_15px_rgba(37,99,235,0.3)] rounded-lg z-0" 
        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
      />
    )}
    <span className="relative z-10 flex items-center space-x-2">
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </span>
  </button>
);

export default App;
