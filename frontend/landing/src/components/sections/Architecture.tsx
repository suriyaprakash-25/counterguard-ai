import { motion } from 'framer-motion';
import { Database, Smartphone, Cpu, Network } from 'lucide-react';

export function Architecture() {
  return (
    <section id="architecture" className="py-32 bg-slate-900 border-y border-slate-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">System Architecture</h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            A robust, decoupled architecture separating the React interface from the autonomous LangGraph engine.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto glass rounded-3xl p-8 border border-slate-800 overflow-hidden">

          <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-purple-500/5 pointer-events-none" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative z-10 text-center">

            {/* Frontend */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="flex flex-col items-center"
            >
              <div className="w-20 h-20 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4">
                <Smartphone className="h-10 w-10 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Frontend</h3>
              <p className="text-sm text-slate-400">React 19, TypeScript, Tailwind, TanStack Query, SSE</p>
            </motion.div>

            {/* Backend */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="flex flex-col items-center"
            >
              <div className="w-20 h-20 rounded-2xl bg-blue-900/50 border border-blue-500/50 flex items-center justify-center mb-4 shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                <Cpu className="h-10 w-10 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Orchestration</h3>
              <p className="text-sm text-slate-400">FastAPI, LangGraph, Planner, Agents, JWT Auth</p>
            </motion.div>

            {/* Database */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="flex flex-col items-center"
            >
              <div className="w-20 h-20 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4 relative">
                <Database className="h-10 w-10 text-purple-400 absolute" />
                <Network className="h-10 w-10 text-purple-400 opacity-0 hover:opacity-100 transition-opacity absolute" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Knowledge</h3>
              <p className="text-sm text-slate-400">Neo4j Graph Database, ChromaDB, GraphRAG</p>
            </motion.div>

          </div>

          {/* Animated Connectors (hidden on mobile) */}
          <div className="hidden md:block absolute top-28 left-[25%] right-[25%] h-0.5 bg-slate-800">
            <motion.div
              animate={{ x: ["0%", "100%"] }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="h-full w-20 bg-gradient-to-r from-transparent via-blue-500 to-transparent"
            />
          </div>

        </div>
      </div>
    </section>
  );
}
