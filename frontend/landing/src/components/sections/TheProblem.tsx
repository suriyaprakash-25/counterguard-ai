import { motion } from 'framer-motion';

const steps = [
  { id: 1, title: 'Counterfeit listing appears', desc: 'A bad actor posts a grey-market product on a major marketplace.' },
  { id: 2, title: 'Customers are affected', desc: 'Brand reputation is damaged as buyers receive inferior goods.' },
  { id: 3, title: 'Manual investigations are slow', desc: 'Human analysts take weeks to connect the dots across fragmented platforms.' },
  { id: 4, title: 'Evidence becomes fragmented', desc: 'Silos prevent analysts from seeing the big picture.' },
  { id: 5, title: 'Fraud networks expand', desc: 'The seller opens three new accounts before the first is banned.' },
  { id: 6, title: 'CounterGuard Automates Everything', desc: 'Agents detect, link, and report the entire fraud ring in minutes.', highlight: true }
];

export function TheProblem() {
  return (
    <section id="problem" className="py-32 bg-slate-950 relative">
      <div className="max-w-3xl mx-auto px-6 text-center mb-20">
        <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">The Old Way is Broken</h2>
        <p className="text-lg text-slate-400">
          Manual brand protection is a losing game of whack-a-mole against sophisticated, automated fraud syndicates.
        </p>
      </div>

      <div className="max-w-4xl mx-auto px-6 relative">
        {/* Vertical Line */}
        <div className="absolute left-[27px] md:left-1/2 top-0 bottom-0 w-px bg-slate-800 -translate-x-1/2" />

        <div className="space-y-12">
          {steps.map((step, index) => (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              key={step.id}
              className={`relative flex flex-col md:flex-row items-start md:items-center gap-8 ${index % 2 === 0 ? 'md:flex-row-reverse' : ''}`}
            >
              {/* Timeline Dot */}
              <div className="absolute left-0 md:left-1/2 w-14 h-14 bg-slate-950 rounded-full flex items-center justify-center -translate-x-1/2 z-10 border border-slate-800">
                <div className={`w-4 h-4 rounded-full ${step.highlight ? 'bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,1)]' : 'bg-slate-700'}`} />
              </div>

              {/* Content Box */}
              <div className={`pl-20 md:pl-0 w-full md:w-1/2 ${index % 2 === 0 ? 'md:pl-16' : 'md:pr-16 text-left md:text-right'}`}>
                <div className={`p-6 rounded-2xl border ${step.highlight ? 'bg-blue-900/20 border-blue-500/50' : 'bg-slate-900 border-slate-800'}`}>
                  <h3 className={`text-xl font-bold mb-2 ${step.highlight ? 'text-blue-400' : 'text-white'}`}>
                    {step.title}
                  </h3>
                  <p className="text-slate-400">{step.desc}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
