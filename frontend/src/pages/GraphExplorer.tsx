import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, ZoomIn, ZoomOut, Maximize, Filter, Download, Info, Activity } from 'lucide-react';
import { apiService } from '../services/api';
import type { GraphData } from '../types/schema';

const GraphExplorer: React.FC<{ accountId?: string }> = ({ accountId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const graphData = await apiService.getGraph(accountId);
        setData(graphData);
      } catch (error) {
        console.error('Failed to fetch graph data:', error);
      } finally {
        setTimeout(() => setLoading(false), 1000);
      }
    };

    fetchGraph();
  }, [accountId]);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const elements = [
      ...data.nodes.map(node => ({
        data: { 
          id: node.id, 
          label: node.label,
          type: node.type 
        }
      })),
      ...data.edges.map((edge, i) => ({
        data: { 
          id: `e${i}`, 
          source: edge.source, 
          target: edge.target,
          type: edge.type,
          weight: edge.amount || 1
        }
      }))
    ];

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': '8px',
            'font-family': 'Outfit',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            'background-color': '#3b82f6',
            'width': 24,
            'height': 24,
            'border-width': 3,
            'border-color': 'rgba(255,255,255,0.1)',
            'overlay-opacity': 0,
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': 300,
          }
        },
        {
          selector: 'node[type="merchant"]',
          style: {
            'background-color': '#10b981',
            'shape': 'hexagon',
            'width': 28,
            'height': 28,
          }
        },
        {
          selector: 'node[type="device"]',
          style: {
            'background-color': '#f59e0b',
            'shape': 'diamond',
            'width': 20,
            'height': 20,
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': 'rgba(255,255,255,0.08)',
            'target-arrow-color': 'rgba(255,255,255,0.08)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8,
            'opacity': 0.4
          }
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#3b82f6',
            'border-width': 4,
            'border-opacity': 0.8,
            'background-color': '#2563eb',
            'line-color': '#3b82f6',
            'target-arrow-color': '#3b82f6',
            'opacity': 1,
            'width': 32,
            'height': 32
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        randomize: false,
        componentSpacing: 120,
        nodeOverlap: 40,
        refresh: 20,
        fit: true,
        padding: 50,
      } as any
    });

    cyRef.current.on('select', 'node', (evt) => {
      setSelectedNode(evt.target.data());
    });

    cyRef.current.on('unselect', 'node', () => {
      setSelectedNode(null);
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [data]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.animate({ 
        fit: { 
          eles: cyRef.current.elements(), 
          padding: 50 
        }, 
        duration: 500 
      });
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-background relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Toolbar */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-16 border-b border-white/5 bg-card/20 backdrop-blur-2xl flex items-center justify-between px-8 z-20"
      >
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
              <Network className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-black uppercase tracking-widest text-white">Topology Visualizer</h2>
              <p className="text-[10px] text-muted-foreground/60 font-medium">Real-time Graph Mapping Engine</p>
            </div>
          </div>
          <div className="h-6 w-[1px] bg-white/10" />
          <div className="flex items-center space-x-6">
            <LegendItem color="bg-blue-500" label="Account" />
            <LegendItem color="bg-emerald-500" label="Merchant" />
            <LegendItem color="bg-amber-500" label="Device" />
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-white/5 p-1 rounded-xl border border-white/5">
          <ControlButton icon={<ZoomIn className="w-4 h-4" />} onClick={handleZoomIn} />
          <ControlButton icon={<ZoomOut className="w-4 h-4" />} onClick={handleZoomOut} />
          <ControlButton icon={<Maximize className="w-4 h-4" />} onClick={handleReset} />
          <div className="h-4 w-[1px] bg-white/10 mx-2" />
          <ControlButton icon={<Filter className="w-4 h-4" />} label="Refine" />
          <ControlButton icon={<Download className="w-4 h-4" />} label="Snapshot" />
        </div>
      </motion.div>

      {/* Graph Area */}
      <div className="flex-1 relative">
        <AnimatePresence>
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-background/60 backdrop-blur-xl"
            >
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="mb-8"
              >
                <Activity className="w-16 h-16 text-blue-500" />
              </motion.div>
              <h3 className="text-xl font-black tracking-tighter glow-text">Reconstructing Graph...</h3>
              <p className="text-xs text-muted-foreground/40 mt-2 font-bold uppercase tracking-widest">Loading stored topology buffers</p>
            </motion.div>
          )}
        </AnimatePresence>
        
        <div ref={containerRef} className="w-full h-full" />

        {/* Floating Details Panel */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ x: 300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 300, opacity: 0 }}
              className="absolute top-8 right-8 w-80 glass-card p-6 rounded-3xl z-20 border-l-4 border-l-blue-500"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-blue-500 mb-1 block">Contextual Node</span>
                  <h3 className="text-xl font-black tracking-tight truncate max-w-[200px]">{selectedNode.label}</h3>
                </div>
                <div className="p-2 bg-white/5 rounded-xl">
                  <Info className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
                    <div className="text-[8px] font-bold uppercase tracking-widest text-muted-foreground/40">Classification</div>
                    <div className="text-xs font-black uppercase text-white mt-1">{selectedNode.type}</div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
                    <div className="text-[8px] font-bold uppercase tracking-widest text-muted-foreground/40">Network Rank</div>
                    <div className="text-xs font-black uppercase text-emerald-500 mt-1">High</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40 border-b border-white/5 pb-2">Technical Registry</h4>
                  <div className="space-y-2">
                    <RegistryItem label="Node Hash" value={selectedNode.id.slice(0, 16) + '...'} />
                    <RegistryItem label="Discovery" value="Auto-Ingested" />
                    <RegistryItem label="Last Update" value={new Date().toLocaleTimeString()} />
                  </div>
                </div>

                <motion.button 
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-blue-600/10 hover:bg-blue-600/20 text-blue-500 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest border border-blue-500/20 transition-all"
                >
                  Expedite Investigation
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

const LegendItem: React.FC<{ color: string; label: string }> = ({ color, label }) => (
  <div className="flex items-center space-x-2">
    <div className={`w-2 h-2 rounded-full ${color} shadow-[0_0_8px_rgba(255,255,255,0.2)]`} />
    <span className="text-[10px] uppercase font-black tracking-widest text-muted-foreground/60">{label}</span>
  </div>
);

const ControlButton: React.FC<{ icon: React.ReactNode; onClick?: () => void; label?: string }> = ({ 
  icon, onClick, label 
}) => (
  <button 
    onClick={onClick}
    className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-all text-muted-foreground hover:text-white"
  >
    {icon}
    {label && <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>}
  </button>
);

const RegistryItem: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-[10px] font-medium text-muted-foreground/60">{label}</span>
    <span className="text-[10px] font-mono text-white/80">{value}</span>
  </div>
);

export default GraphExplorer;
