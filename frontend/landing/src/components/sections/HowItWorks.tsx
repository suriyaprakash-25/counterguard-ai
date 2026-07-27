import { motion } from 'framer-motion';
import { BrainCircuit, Search, Database, Network, ShieldAlert, FileCheck2 } from 'lucide-react';

const workflow = [
  { icon: BrainCircuit, title: 'AI Planner', desc: 'Analyzes intent and assigns agents.' },
  { icon: Search, title: 'Marketplace Intelligence', desc: 'Agents scrape and parse public listings.' },
  { icon: Database, title: 'Memory Construction', desc: 'Vectorizes evidence into ChromaDB.' },
  { icon: Network, title: 'GraphRAG Integration', desc: 'Extracts entities into Neo4j graph.' },
  { icon: ShieldAlert, title: 'Risk Analysis', desc: 'Evaluates severity and fraud ring scale.' },
  { icon: FileCheck2, title: 'Explainable Report', desc: 'Generates final human-readable brief.' }
];

export function HowItWorks() {
  return (
    <section id="workflow" className="py-32 bg-slate-900 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">How CounterGuard Works</h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            A complete autonomous pipeline powered by LangGraph, navigating from raw suspicion to deterministic action.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 relative">
          {workflow.map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="glass p-8 rounded-2xl relative group hover:bg-slate-800/50 transition-colors"
            >
              <div className="w-14 h-14 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-center justify-center mb-6 text-blue-400 group-hover:scale-110 group-hover:text-cyan-400 transition-all">
                <item.icon className="h-7 w-7" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3 flex items-center justify-between">
                {item.title}
                <span className="text-slate-700 font-mono text-sm">0{i+1}</span>
              </h3>
              <p className="text-slate-400">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
