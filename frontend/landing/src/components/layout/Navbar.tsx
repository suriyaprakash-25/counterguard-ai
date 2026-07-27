import { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass py-3' : 'bg-transparent py-5'}`}>
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 bg-blue-600 rounded-xl flex items-center justify-center transform rotate-3 shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            <Shield className="h-6 w-6 text-white -rotate-3" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">CounterGuard</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#workflow" className="hover:text-white transition-colors">Workflow</a>
          <a href="#roadmap" className="hover:text-white transition-colors">Roadmap</a>
        </div>

        <div className="flex items-center gap-4">
          <a href="https://github.com/counterguard-ai" target="_blank" rel="noreferrer" className="hidden lg:block text-sm font-medium text-slate-300 hover:text-white transition-colors">
            GitHub
          </a>
          <button className="bg-white text-slate-950 px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-slate-200 transition-colors">
            Get Started
          </button>
        </div>
      </div>
    </nav>
  );
}
