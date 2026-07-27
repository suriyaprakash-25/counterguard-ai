import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { Hero } from './components/sections/Hero';
import { TheProblem } from './components/sections/TheProblem';
import { HowItWorks } from './components/sections/HowItWorks';
import { Features } from './components/sections/Features';
import { Architecture } from './components/sections/Architecture';
import { DeepDives } from './components/sections/DeepDives';
import { Validation } from './components/sections/Validation';

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 selection:bg-blue-500/30 selection:text-blue-200">
      <Navbar />

      <main>
        <Hero />
        <TheProblem />
        <HowItWorks />
        <Features />
        <Architecture />
        <DeepDives />
        <Validation />
      </main>

      <Footer />
    </div>
  );
}

export default App;
