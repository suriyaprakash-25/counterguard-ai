import { motion } from 'framer-motion';
import { ArrowRight, ShieldCheck, Network, Activity } from 'lucide-react';

export function Hero() {
  return (
    <section className="relative min-h-screen pt-32 pb-20 flex items-center overflow-hidden">
      {/* Animated Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[500px] opacity-30 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600 rounded-full mix-blend-screen filter blur-[100px] animate-blob" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000" />
        <div className="absolute -bottom-8 left-1/3 w-96 h-96 bg-purple-600 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-4000" />
      </div>

      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 relative z-10">

        {/* Left: Copy */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col justify-center"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-blue-500/20 text-blue-400 text-sm font-medium mb-6 w-fit">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Version 1.0 is now live
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.1]">
            Autonomous <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-500">
              Counterfeit & Grey-Market
            </span><br/>
            Intelligence Platform
          </h1>

          <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-lg leading-relaxed">
            CounterGuard deploys multi-agent AI to map, investigate, and disrupt global fraud networks in real-time using GraphRAG and autonomous reasoning.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <button className="bg-white text-slate-950 px-8 py-4 rounded-full font-semibold hover:bg-slate-200 transition-colors flex items-center justify-center gap-2">
              Explore Platform <ArrowRight className="h-5 w-5" />
            </button>
            <button className="glass text-white px-8 py-4 rounded-full font-semibold hover:bg-white/10 transition-colors flex items-center justify-center">
              View Architecture
            </button>
          </div>
        </motion.div>

        {/* Right: Abstract UI Mock */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="relative hidden lg:block"
        >
          <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/10 to-purple-500/10 rounded-2xl transform rotate-3" />
          <div className="relative glass rounded-2xl border border-slate-800 p-6 shadow-2xl h-full min-h-[500px]">
            {/* Mock Dashboard Header */}
            <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-800">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <div className="flex gap-4">
                <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-1 rounded">Agent-7 Active</span>
              </div>
            </div>

            {/* Mock Content */}
            <div className="space-y-4">
              <motion.div
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-4"
              >
                <div className="p-3 rounded-lg bg-blue-500/20 text-blue-400"><Activity className="h-6 w-6" /></div>
                <div>
                  <h4 className="text-white font-medium">Intercepted Listing</h4>
                  <p className="text-xs text-slate-400 mt-1">Amazon: iPhone 15 Pro Max Clone</p>
                </div>
              </motion.div>

              <motion.div
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-4 ml-8"
              >
                <div className="p-3 rounded-lg bg-cyan-500/20 text-cyan-400"><Network className="h-6 w-6" /></div>
                <div>
                  <h4 className="text-white font-medium">Graph Extracted</h4>
                  <p className="text-xs text-slate-400 mt-1">Found 12 linked sellers via GraphRAG</p>
                </div>
              </motion.div>

              <motion.div
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 1.1 }}
                className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-4 ml-16"
              >
                <div className="p-3 rounded-lg bg-purple-500/20 text-purple-400"><ShieldCheck className="h-6 w-6" /></div>
                <div>
                  <h4 className="text-white font-medium">Takedown Recommended</h4>
                  <p className="text-xs text-slate-400 mt-1">Confidence Score: 98.4%</p>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
