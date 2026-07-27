import { motion } from 'framer-motion';
import { TerminalSquare } from 'lucide-react';

const stats = [
  { value: '100%', label: 'Production Ready' },
  { value: '24/7', label: 'Continuous Monitoring' },
  { value: '<2s', label: 'Real-Time Streaming' },
  { value: 'Multi', label: 'Agent Architecture' },
];

const techStack = [
  'React 19', 'TypeScript', 'FastAPI', 'LangGraph',
  'Neo4j', 'GraphRAG', 'TanStack Query', 'Docker',
  'GitHub Actions', 'WebSockets', 'JWT', 'Tailwind CSS'
];

const roadmap = [
  { sprint: 'Sprint 1–15', title: 'Core Platform Foundation', complete: true },
  { sprint: 'Sprint 16.1', title: 'API Integration & Proxies', complete: true },
  { sprint: 'Sprint 16.2', title: 'Live Agent Investigations', complete: true },
  { sprint: 'Sprint 16.3', title: 'Real-Time SSE Streaming', complete: true },
  { sprint: 'Sprint 16.4', title: 'Enterprise Auth & RBAC', complete: true },
  { sprint: 'Sprint 16.5', title: 'Version 1.0 Production Release', complete: true, active: true },
];

export function Validation() {
  return (
    <section id="roadmap" className="py-32 bg-slate-900 border-t border-slate-800">

      {/* 1. Statistics */}
      <div className="max-w-7xl mx-auto px-6 mb-32">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-blue-400 to-purple-500 mb-2">
                {stat.value}
              </div>
              <div className="text-sm font-medium text-slate-400 uppercase tracking-widest">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 2. Tech Stack */}
      <div className="max-w-7xl mx-auto px-6 mb-32 text-center">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest mb-8">Powered by Modern Enterprise Technology</h3>
        <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
          {techStack.map((tech) => (
            <div key={tech} className="px-4 py-2 rounded-full border border-slate-700 bg-slate-800/50 text-slate-300 text-sm font-medium hover:bg-slate-700 hover:text-white transition-colors">
              {tech}
            </div>
          ))}
        </div>
      </div>

      {/* 3. Development Roadmap */}
      <div className="max-w-3xl mx-auto px-6 mb-32">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">The Journey to V1.0</h2>
          <p className="text-slate-400">A rigorous engineering sprint schedule to deliver enterprise grade capability.</p>
        </div>

        <div className="space-y-4">
          {roadmap.map((item, i) => (
            <div key={i} className={`flex items-center gap-6 p-4 rounded-xl border ${item.active ? 'bg-blue-900/20 border-blue-500/50' : 'bg-slate-900 border-slate-800'}`}>
              <div className={`text-xs font-mono px-2 py-1 rounded ${item.active ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                {item.sprint}
              </div>
              <div className={`font-medium ${item.active ? 'text-white' : 'text-slate-300'}`}>
                {item.title}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. CTA */}
      <div className="max-w-5xl mx-auto px-6">
        <div className="relative glass rounded-3xl border border-blue-500/30 overflow-hidden text-center p-12 md:p-20 shadow-[0_0_50px_rgba(59,130,246,0.1)]">
          <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 to-slate-900/50" />
          <div className="relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Ready to transform your investigations?</h2>
            <p className="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
              Deploy CounterGuard today to autonomously map, monitor, and dismantle grey-market operations before they impact your brand.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button className="bg-blue-600 text-white px-8 py-4 rounded-full font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                <TerminalSquare className="h-5 w-5" /> Launch Platform
              </button>
              <button className="bg-slate-800 text-white px-8 py-4 rounded-full font-semibold hover:bg-slate-700 transition-colors flex items-center justify-center gap-2 border border-slate-700">
                View GitHub
              </button>
            </div>
          </div>
        </div>
      </div>

    </section>
  );
}
