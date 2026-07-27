import { motion } from 'framer-motion';
import { Search, Brain, ShieldAlert, CheckCircle2, MapPin, Phone, User, Package } from 'lucide-react';

export function DeepDives() {
  return (
    <section className="py-32 bg-slate-950 border-t border-slate-800 overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 space-y-32">

        {/* 1. Investigation Workflow */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Autonomous Workflows</h2>
            <p className="text-lg text-slate-400 mb-8">
              Watch as LangGraph agents independently formulate plans, scrape public data, vector-search memory, and construct reports. You just review the results.
            </p>
            <ul className="space-y-6">
              {[
                { icon: Brain, title: 'Planning', desc: 'Agent evaluates initial suspicion and drafts execution plan.' },
                { icon: Search, title: 'Evidence Collection', desc: 'Parallel agents scrape images, reviews, and seller details.' },
                { icon: ShieldAlert, title: 'Risk Analysis', desc: 'Scoring against historical memory and graph topology.' }
              ].map((item, i) => (
                <li key={i} className="flex gap-4">
                  <div className="mt-1 h-10 w-10 rounded-lg bg-blue-900/50 flex items-center justify-center border border-blue-500/50 shrink-0 text-blue-400">
                    <item.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">{item.title}</h4>
                    <p className="text-slate-400 text-sm mt-1">{item.desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="relative h-[400px] glass rounded-3xl border border-slate-800 p-8 shadow-2xl flex flex-col justify-center">
            {/* Animated Timeline */}
            <div className="absolute left-12 top-12 bottom-12 w-0.5 bg-slate-800" />
            <motion.div
              animate={{ height: ["0%", "100%"] }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              className="absolute left-12 top-12 bottom-12 w-0.5 bg-gradient-to-b from-blue-500 via-cyan-400 to-transparent"
            />

            <div className="space-y-8 pl-12 relative z-10">
              <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} className="glass p-4 rounded-xl border border-slate-700 bg-slate-900 text-sm text-slate-300">
                <span className="text-blue-400 font-mono text-xs mr-2">[00:00]</span> Planner Agent initiated.
              </motion.div>
              <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="glass p-4 rounded-xl border border-slate-700 bg-slate-900 text-sm text-slate-300">
                <span className="text-blue-400 font-mono text-xs mr-2">[00:02]</span> Memory Agent located 3 matching records.
              </motion.div>
              <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="glass p-4 rounded-xl border border-slate-700 bg-slate-900 text-sm text-slate-300">
                <span className="text-cyan-400 font-mono text-xs mr-2">[00:05]</span> GraphRAG Agent extracted 5 new nodes.
              </motion.div>
              <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 }} className="glass p-4 rounded-xl border-blue-500/50 bg-blue-900/20 text-sm text-white font-medium flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-400" /> Investigation complete. Report ready.
              </motion.div>
            </div>
          </div>
        </div>

        {/* 2. Knowledge Graph Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center lg:flex-row-reverse">
          <div className="order-1 lg:order-2">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Interactive Graph Intelligence</h2>
            <p className="text-lg text-slate-400 mb-8">
              CounterGuard utilizes Neo4j to build a massive Knowledge Graph of all marketplace entities. We don't just ban single accounts; we trace and eradicate entire fraud rings.
            </p>
            <button className="text-blue-400 font-semibold hover:text-blue-300 flex items-center gap-2 transition-colors">
              Read our GraphRAG Whitepaper →
            </button>
          </div>

          <div className="order-2 lg:order-1 relative h-[450px] glass rounded-3xl border border-slate-800 shadow-2xl overflow-hidden flex items-center justify-center">
            {/* Simulated Graph Nodes */}
            <div className="absolute inset-0 bg-slate-900/50" />

            <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 4, repeat: Infinity }} className="absolute z-10 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-red-500/20 rounded-full border border-red-500 flex items-center justify-center shadow-[0_0_30px_rgba(239,68,68,0.3)]">
              <User className="h-8 w-8 text-red-500" />
            </motion.div>

            <motion.div animate={{ x: [0, 10, 0] }} transition={{ duration: 5, repeat: Infinity }} className="absolute z-10 top-1/4 left-1/3 w-14 h-14 bg-slate-800 rounded-full border border-slate-600 flex items-center justify-center">
              <Phone className="h-5 w-5 text-slate-400" />
            </motion.div>

            <motion.div animate={{ y: [0, 15, 0] }} transition={{ duration: 6, repeat: Infinity }} className="absolute z-10 bottom-1/4 right-1/4 w-16 h-16 bg-slate-800 rounded-full border border-slate-600 flex items-center justify-center">
              <MapPin className="h-6 w-6 text-slate-400" />
            </motion.div>

            <motion.div animate={{ x: [0, -15, 0] }} transition={{ duration: 5.5, repeat: Infinity }} className="absolute z-10 top-1/3 right-1/3 w-14 h-14 bg-slate-800 rounded-full border border-slate-600 flex items-center justify-center">
              <Package className="h-5 w-5 text-slate-400" />
            </motion.div>

            {/* Simulated SVG Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="50%" x2="33%" y2="25%" stroke="rgba(239,68,68,0.4)" strokeWidth="2" strokeDasharray="5,5" />
              <line x1="50%" y1="50%" x2="75%" y2="75%" stroke="rgba(239,68,68,0.4)" strokeWidth="2" />
              <line x1="50%" y1="50%" x2="66%" y2="33%" stroke="rgba(239,68,68,0.4)" strokeWidth="2" />
            </svg>
          </div>
        </div>

        {/* 3. Explainability */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Unmatched Explainability</h2>
            <p className="text-lg text-slate-400 mb-8">
              AI shouldn't be a black box. CounterGuard provides 100% transparent reasoning for every decision, citing exact evidence fragments and confidence scores.
            </p>
          </div>

          <motion.div
            whileHover={{ scale: 1.02 }}
            className="relative glass rounded-3xl border border-slate-800 p-8 shadow-2xl bg-gradient-to-br from-slate-900 to-slate-950"
          >
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Brain className="h-6 w-6 text-purple-400" /> AI Reasoning Engine
            </h3>

            <p className="text-slate-300 font-medium mb-4">Why was this seller flagged as Critical Risk?</p>

            <ul className="space-y-3 mb-8">
              <li className="flex items-center gap-3 text-sm text-slate-400 bg-slate-900 p-3 rounded-lg border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                Shared phone number with banned entity <span className="font-mono text-xs text-blue-400">#E-910</span>
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-400 bg-slate-900 p-3 rounded-lg border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                Graph topology indicates degree-1 connection to Fraud Ring B
              </li>
              <li className="flex items-center gap-3 text-sm text-slate-400 bg-slate-900 p-3 rounded-lg border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                Image forensic matching on 4 distinct product listings
              </li>
            </ul>

            <div className="flex items-center justify-between border-t border-slate-800 pt-6">
              <span className="text-slate-400 font-medium">Confidence Score</span>
              <span className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-500">
                98.4%
              </span>
            </div>
          </motion.div>
        </div>

      </div>
    </section>
  );
}
