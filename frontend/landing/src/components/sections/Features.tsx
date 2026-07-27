import { motion } from 'framer-motion';
import {
  Bot, Network, BrainCircuit, GlobeLock, AlertTriangle,
  Activity, ShieldCheck, Lock, Users, Server
} from 'lucide-react';

const features = [
  { icon: Bot, title: 'Autonomous Agents', desc: 'LangGraph-powered agents execute complex plans without human intervention.' },
  { icon: Network, title: 'Knowledge Graph', desc: 'Neo4j backend maps hidden seller relationships and fraud rings.' },
  { icon: BrainCircuit, title: 'GraphRAG Context', desc: 'Retrieval Augmented Generation infused with graph topology.' },
  { icon: GlobeLock, title: 'Continuous Monitoring', desc: '24/7 scanning of targeted marketplace URLs and entity changes.' },
  { icon: ShieldCheck, title: 'Explainability', desc: 'Every AI decision is logged with supporting evidence and confidence scores.' },
  { icon: Activity, title: 'Real-Time Streaming', desc: 'WebSocket/SSE pipelines beam agent activity straight to your dashboard.' },
  { icon: AlertTriangle, title: 'Smart Alerts', desc: 'Threshold-based notifications when a fraud ring risk score spikes.' },
  { icon: Lock, title: 'Auth & Security', desc: 'Enterprise-grade JWT authentication and strict access controls.' },
  { icon: Users, title: 'RBAC', desc: 'Role-Based Access Control dividing Analysts, Investigators, and Admins.' },
  { icon: Server, title: 'Production Ready', desc: 'Fully containerized with Docker, CI/CD, and structured logging.' },
];

export function Features() {
  return (
    <section id="features" className="py-32 bg-slate-950 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[600px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Platform Capabilities</h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            A comprehensive suite of tools built for enterprise fraud teams. From initial suspicion to final enforcement.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: i * 0.05 }}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/80 transition-all group"
            >
              <feature.icon className="h-8 w-8 text-slate-400 group-hover:text-blue-400 transition-colors mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
