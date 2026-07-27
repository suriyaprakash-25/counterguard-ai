import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-slate-800/50 bg-slate-950 pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
        <div className="md:col-span-1 text-slate-400">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="h-6 w-6 text-blue-500" />
            <span className="text-lg font-bold text-white">CounterGuard</span>
          </div>
          <p className="text-sm leading-relaxed mb-6">
            The autonomous intelligence platform for disrupting global counterfeit networks. Built for scale, security, and precision.
          </p>
          <div className="flex gap-4">
            <a href="#" className="hover:text-white transition-colors">GitHub</a>
            <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
            <a href="#" className="hover:text-white transition-colors">Twitter</a>
          </div>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-4">Platform</h4>
          <ul className="space-y-3 text-sm text-slate-400">
            <li><a href="#" className="hover:text-white transition-colors">Multi-Agent Engine</a></li>
            <li><a href="#" className="hover:text-white transition-colors">GraphRAG</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Real-Time Intelligence</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Enterprise Security</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-4">Developers</h4>
          <ul className="space-y-3 text-sm text-slate-400">
            <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
            <li><a href="#" className="hover:text-white transition-colors">API Reference</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Architecture</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Open Source</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-4">Company</h4>
          <ul className="space-y-3 text-sm text-slate-400">
            <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 border-t border-slate-800/50 pt-8 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500">
        <p>&copy; {new Date().getFullYear()} CounterGuard Intelligence. All rights reserved.</p>
        <div className="flex gap-6 mt-4 md:mt-0">
          <a href="#" className="hover:text-slate-300">Privacy Policy</a>
          <a href="#" className="hover:text-slate-300">Terms of Service</a>
        </div>
      </div>
    </footer>
  );
}
