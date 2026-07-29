import { useState, useMemo } from 'react';
import { Button } from '../../components/common/Button';
import { useCreateInvestigation } from '../../hooks/useInvestigations';
import { useNavigate } from 'react-router-dom';
import { normalizeTarget } from '../../services/target_normalization';
import {
  ShieldAlert,
  Zap,
  Layers,
  Sparkles,
  Bot,
  Search,
  CheckCircle2,
  Sliders,
  ChevronDown,
  ChevronUp,
  Cpu,
  Globe,
  Store,
  Tag,
  Link,
  FileText,
  Clock,
  ArrowRight,
  X
} from 'lucide-react';

interface CreateInvestigationDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const TARGET_TYPES = [
  { id: 'Marketplace Product URL', icon: Link, placeholder: 'https://www.amazon.com/dp/B08N5WRWNW' },
  { id: 'Product Name', icon: Tag, placeholder: 'e.g. Nothing Phone 2a' },
  { id: 'Brand + Model', icon: Layers, placeholder: 'e.g. Sony WH-1000XM5' },
  { id: 'Seller Store URL', icon: Store, placeholder: 'e.g. https://ebay.com/usr/techdeals-global' },
  { id: 'Seller Username', icon: Store, placeholder: 'e.g. TechDeals_Global_88' },
  { id: 'ASIN / SKU', icon: Tag, placeholder: 'e.g. B08N5WRWNW or SKU-99482' },
  { id: 'Domain Name', icon: Globe, placeholder: 'e.g. techdeals-outlet-store.com' },
  { id: 'Free Text Directives', icon: FileText, placeholder: 'Describe target entity or listing...' }
];

const MISSION_TYPES = [
  {
    id: 'Counterfeit Detection',
    title: 'Counterfeit Detection',
    badge: 'High Precision',
    description: 'Autonomous multi-agent verification of product authenticity, seller trust, and packaging anomalies.',
    agentsCount: 7,
    runtime: '~60s'
  },
  {
    id: 'Grey Market Analysis',
    title: 'Grey Market Analysis',
    badge: 'Channel Audit',
    description: 'Detect unauthorized distribution channels, regional pricing diversion, and imported SKU mismatches.',
    agentsCount: 5,
    runtime: '~45s'
  },
  {
    id: 'Seller Verification',
    title: 'Seller Verification',
    badge: 'Merchant Audit',
    description: 'WHOIS domain lookup, seller registration age, store reputation, and cross-platform identity resolution.',
    agentsCount: 4,
    runtime: '~30s'
  },
  {
    id: 'Brand Protection',
    title: 'Brand Protection',
    badge: 'IP Defense',
    description: 'Identify unauthorized brand trademark usage, unofficial logo usage, and fake flagship outlets.',
    agentsCount: 5,
    runtime: '~45s'
  },
  {
    id: 'Marketplace Intelligence',
    title: 'Marketplace Intelligence',
    badge: 'Multi-Store Search',
    description: 'Aggregate baseline catalog specs across Amazon, Best Buy, Walmart, Flipkart, and official brand stores.',
    agentsCount: 6,
    runtime: '~45s'
  },
  {
    id: 'Price Intelligence',
    title: 'Price Intelligence',
    badge: 'Baseline Comparison',
    description: 'Deep price distribution analysis, MSRP deviation scoring, and verified genuine deal recommendation.',
    agentsCount: 4,
    runtime: '~30s'
  }
];

const MISSION_OBJECTIVES = [
  { id: 'Verify Product Authenticity', label: 'Verify Product Authenticity', defaultChecked: true, comingSoon: false },
  { id: 'Verify Seller Identity & Trust', label: 'Verify Seller Identity & Trust', defaultChecked: true, comingSoon: false },
  { id: 'Trademark Registry Verification', label: 'Trademark Registry Verification', defaultChecked: true, comingSoon: false },
  { id: 'Domain WHOIS & DNS Reputation', label: 'Domain WHOIS & DNS Reputation', defaultChecked: true, comingSoon: false },
  { id: 'Cross-Provider Price Baseline Analysis', label: 'Cross-Provider Price Baseline Analysis', defaultChecked: true, comingSoon: false },
  { id: 'Historical Pattern Matching & Fraud Memory', label: 'Historical Pattern Matching & Fraud Memory', defaultChecked: false, comingSoon: true },
  { id: 'Recommend Genuine Verified Alternatives', label: 'Recommend Genuine Verified Alternatives', defaultChecked: true, comingSoon: false },
  { id: 'Grey Market & Regional Variance Detection', label: 'Grey Market & Regional Mismatch', defaultChecked: false, comingSoon: false },
  { id: 'Review Authenticity & NLP Analysis', label: 'Review NLP & Image Verification', defaultChecked: false, comingSoon: false },
  { id: 'Graph Network Entity Resolution', label: 'Knowledge Graph Entity Resolution', defaultChecked: false, comingSoon: true }
];

const PLANNING_STRATEGIES = [
  {
    id: 'Fast Investigation',
    title: 'Fast Investigation',
    icon: Zap,
    runtime: '~15s',
    agents: 4,
    providers: 2,
    desc: 'Lightweight parallel scan for urgent preliminary triage.'
  },
  {
    id: 'Balanced Investigation',
    title: 'Balanced Investigation',
    icon: Sliders,
    runtime: '~30s',
    agents: 5,
    providers: 4,
    desc: 'Standard multi-agent execution with balanced depth and latency.'
  },
  {
    id: 'Deep Intelligence',
    title: 'Deep Intelligence',
    icon: Cpu,
    runtime: '~60s',
    agents: 7,
    providers: 6,
    desc: 'Comprehensive multi-agent swarm with 6-provider concurrent retrieval, vector memory, and graph RAG.'
  },
  {
    id: 'Full Autonomous Swarm',
    title: 'Full Autonomous Swarm',
    icon: Bot,
    runtime: '~90s',
    agents: 9,
    providers: 6,
    desc: 'Exhaustive cyber-intelligence collection with full graph entity resolution and threat network mapping.'
  }
];

const SWARM_AGENTS = [
  { name: 'PlanningAgent', role: 'Strategy & Route Optimization', icon: Cpu },
  { name: 'PriceAgent', role: 'Historical Price Anomaly Engine', icon: Tag },
  { name: 'SellerAgent', role: 'WHOIS & Merchant Reputation Audit', icon: Store },
  { name: 'BrandAgent', role: 'Trademark Registry & Catalog Verification', icon: Layers },
  { name: 'ReviewAgent', role: 'NLP Sentiment & Reverse Image Search', icon: ShieldAlert },
  { name: 'TrustedProductAgent', role: 'Concurrent Multi-Provider Retrieval', icon: Search },
  { name: 'CoordinatorAgent', role: 'Blackboard Multi-Agent Consensus', icon: Bot },
  { name: 'GraphAgent', role: 'Knowledge Graph Threat Entity Extractor', icon: Layers },
  { name: 'MemoryAgent', role: 'Chroma Vector Episode Memory', icon: Sparkles }
];

export function CreateInvestigationDialog({ isOpen, onClose }: CreateInvestigationDialogProps) {
  const navigate = useNavigate();
  const { mutate: createInvestigation, isPending } = useCreateInvestigation();

  const [activeTab, setActiveTab] = useState<'target' | 'mission' | 'strategy' | 'advanced'>('target');

  // Form State
  const [targetType, setTargetType] = useState('Marketplace Product URL');
  const [targetValue, setTargetValue] = useState('');
  const [investigationName, setInvestigationName] = useState('');
  const [isNameEdited, setIsNameEdited] = useState(false);

  const [brand, setBrand] = useState('');
  const [product, setProduct] = useState('');
  const [marketplace, setMarketplace] = useState('Amazon');
  const [seller, setSeller] = useState('');

  const [investigationType, setInvestigationType] = useState('Counterfeit Detection');
  const [selectedObjectives, setSelectedObjectives] = useState<string[]>(
    MISSION_OBJECTIVES.filter(o => o.defaultChecked).map(o => o.id)
  );
  const [plannerStrategy, setPlannerStrategy] = useState('Deep Intelligence');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'critical'>('high');

  const [notes, setNotes] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [advancedOptions, setAdvancedOptions] = useState({
    region: 'Global',
    language: 'English',
    searchDepth: 'Deep',
    maxProviders: 6,
    timeoutSeconds: 60,
    enableMemory: true,
    enableGraph: true
  });

  // Auto-parse Brand/Model/Marketplace and generate Mission Name
  const handleTargetValueChange = (val: string) => {
    setTargetValue(val);

    if (!val.trim()) {
      if (!isNameEdited) setInvestigationName('');
      return;
    }

    // Auto-detect Marketplace
    let detectedMarketplace = marketplace;
    if (val.includes('amazon.')) {
      detectedMarketplace = 'Amazon';
    } else if (val.includes('ebay.')) {
      detectedMarketplace = 'eBay';
    } else if (val.includes('bestbuy.')) {
      detectedMarketplace = 'BestBuy';
    } else if (val.includes('walmart.')) {
      detectedMarketplace = 'Walmart';
    } else if (val.includes('flipkart.')) {
      detectedMarketplace = 'Flipkart';
    } else if (val.includes('tradeindia.')) {
      detectedMarketplace = 'TradeIndia';
    } else if (val.includes('meesho.')) {
      detectedMarketplace = 'Meesho';
    } else if (val.includes('ajio.')) {
      detectedMarketplace = 'AJIO';
    } else if (val.includes('myntra.')) {
      detectedMarketplace = 'Myntra';
    } else if (val.startsWith('http://') || val.startsWith('https://')) {
      try {
        const u = new URL(val);
        const host = u.hostname.replace(/^www\./, '').split('.')[0];
        detectedMarketplace = host.charAt(0).toUpperCase() + host.slice(1);
      } catch {
        detectedMarketplace = 'Global';
      }
    }
    setMarketplace(detectedMarketplace);

    // Auto-normalize title & extract Brand / Product
    const norm = normalizeTarget(val);

    if (val.startsWith('http://') || val.startsWith('https://')) {
      const cleanTitle = norm.displayTitle;
      const words = cleanTitle.split(' ');

      // Infer Brand and Model if not already typed
      let inferredBrand = brand;
      let inferredProd = product;

      if (!brand) {
        if (cleanTitle.toLowerCase().includes('nothing') || cleanTitle.toLowerCase().includes('cmf')) {
          inferredBrand = 'Nothing';
        } else if (cleanTitle.toLowerCase().includes('sony')) {
          inferredBrand = 'Sony';
        } else if (cleanTitle.toLowerCase().includes('apple') || cleanTitle.toLowerCase().includes('iphone') || cleanTitle.toLowerCase().includes('airpods')) {
          inferredBrand = 'Apple';
        } else {
          inferredBrand = words[0] || 'Generic Brand';
        }
        setBrand(inferredBrand);
      }

      if (!product) {
        if (cleanTitle.toLowerCase().includes('cmf') && cleanTitle.toLowerCase().includes('buds')) {
          inferredProd = 'CMF Buds';
        } else {
          inferredProd = words.slice(1).join(' ') || words[0] || 'Target Listing';
        }
        setProduct(inferredProd);
      }

      if (!isNameEdited) {
        setInvestigationName(`search://${inferredBrand || 'Brand'}/${inferredProd || cleanTitle}`);
      }
    } else if (val.trim() && !isNameEdited) {
      const words = val.trim().split(' ');
      const inferredBrand = words[0] || 'Brand';
      const inferredProd = words.slice(1).join(' ') || words[0];
      if (!brand) setBrand(inferredBrand);
      if (!product) setProduct(inferredProd);
      setInvestigationName(`search://${inferredBrand}/${inferredProd}`);
    }
  };

  const toggleObjective = (id: string) => {
    setSelectedObjectives(prev =>
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const selectedStrategyInfo = useMemo(() => {
    return PLANNING_STRATEGIES.find(s => s.id === plannerStrategy) || PLANNING_STRATEGIES[2];
  }, [plannerStrategy]);

  const isValid = targetValue.trim().length > 0 || (brand.trim().length > 0 && product.trim().length > 0);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;

    const finalName = investigationName || (targetValue ? `Mission: ${targetValue.substring(0, 24)}` : `search://${brand || 'Brand'}/${product || 'Product'}`);

    const payload = {
      name: finalName,
      brand: brand || 'Generic Brand',
      marketplace: marketplace || 'Global',
      product: product || 'Target Model',
      seller: seller || (targetValue.includes('http') ? targetValue : 'Global Seller'),
      plannerPriority: priority,
      notes: notes,
      investigation_type: investigationType,
      planner_strategy: plannerStrategy,
      objectives: selectedObjectives,
      target_type: targetType,
      target_value: targetValue,
      advanced_options: advancedOptions
    };

    createInvestigation(payload, {
      onSuccess: (data) => {
        onClose();
        navigate(`/investigations/${data.id}`);
      },
      onError: (err) => {
        console.error('Failed to launch autonomous mission:', err);
      }
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md p-4 overflow-y-auto">
      <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-4xl border border-border mt-6 mb-6 overflow-hidden flex flex-col max-h-[90vh]">

        {/* Modal Header */}
        <div className="p-6 border-b border-border bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white flex justify-between items-center shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light shadow-inner">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight">AI Mission Planner</h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                  Swarm Engine v2.4
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-0.5">
                Configure autonomous intelligence objectives, target parameters, and multi-agent execution strategy.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-slate-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Step Navigation Bar */}
        <div className="flex border-b border-border bg-slate-50 shrink-0 text-xs font-semibold uppercase tracking-wider text-slate-600">
          <button
            type="button"
            onClick={() => setActiveTab('target')}
            className={`flex-1 py-3 px-4 flex items-center justify-center gap-2 border-b-2 transition-colors ${
              activeTab === 'target'
                ? 'border-primary text-primary bg-surface font-bold'
                : 'border-transparent hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <TargetStepIcon isValid={targetValue.length > 0} /> 1. Mission Target & Context
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('mission')}
            className={`flex-1 py-3 px-4 flex items-center justify-center gap-2 border-b-2 transition-colors ${
              activeTab === 'mission'
                ? 'border-primary text-primary bg-surface font-bold'
                : 'border-transparent hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <ShieldAlert className="h-4 w-4" /> 2. Type & Objectives ({selectedObjectives.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('strategy')}
            className={`flex-1 py-3 px-4 flex items-center justify-center gap-2 border-b-2 transition-colors ${
              activeTab === 'strategy'
                ? 'border-primary text-primary bg-surface font-bold'
                : 'border-transparent hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Zap className="h-4 w-4" /> 3. Swarm Strategy
          </button>
        </div>

        {/* Main Content Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto flex flex-col justify-between">
          <div className="p-6 space-y-6">

            {/* TAB 1: MISSION TARGET & CONTEXT */}
            {activeTab === 'target' && (
              <div className="space-y-6 animate-fadeIn">
                {/* Target Type Chips */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Select Target Input Type
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {TARGET_TYPES.map(tt => {
                      const IconComp = tt.icon;
                      const isSelected = targetType === tt.id;
                      return (
                        <button
                          key={tt.id}
                          type="button"
                          onClick={() => setTargetType(tt.id)}
                          className={`flex items-center gap-2 p-2.5 rounded-lg border text-left text-xs font-medium transition-all ${
                            isSelected
                              ? 'border-primary bg-primary/5 text-primary ring-1 ring-primary'
                              : 'border-border bg-surface hover:bg-slate-50 text-slate-700'
                          }`}
                        >
                          <IconComp className={`h-4 w-4 shrink-0 ${isSelected ? 'text-primary' : 'text-slate-400'}`} />
                          <span className="truncate">{tt.id}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Target Value Input */}
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Mission Target Input <span className="text-red-500">*</span>
                    </label>
                    <span className="text-[10px] text-muted font-mono">Auto-extracts Brand, Model & Store</span>
                  </div>
                  <div className="relative">
                    <input
                      required
                      type="text"
                      value={targetValue}
                      onChange={e => handleTargetValueChange(e.target.value)}
                      placeholder={TARGET_TYPES.find(t => t.id === targetType)?.placeholder || 'Enter listing URL or target details...'}
                      className="w-full p-3 pl-10 border border-border rounded-xl text-sm bg-slate-50/50 focus:bg-surface focus:ring-2 focus:ring-primary focus:border-transparent font-mono"
                    />
                    <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3.5" />
                  </div>
                </div>

                {/* Mission Name & Context Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-border">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Auto-Generated Mission Title
                    </label>
                    <input
                      type="text"
                      value={investigationName}
                      onChange={e => {
                        setInvestigationName(e.target.value);
                        setIsNameEdited(true);
                      }}
                      placeholder="e.g. search://Apple/iPhone 15 Pro"
                      className="w-full p-2.5 border border-border rounded-lg text-sm bg-surface font-semibold text-slate-900"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Target Marketplace
                    </label>
                    <select
                      value={marketplace}
                      onChange={e => setMarketplace(e.target.value)}
                      className="w-full p-2.5 border border-border rounded-lg text-sm bg-surface font-medium text-slate-900"
                    >
                      <option value="Amazon">Amazon (Global / US / IN)</option>
                      <option value="eBay">eBay Authorized Marketplace</option>
                      <option value="BestBuy">Best Buy Stores</option>
                      <option value="Walmart">Walmart Retail Online</option>
                      <option value="Flipkart">Flipkart Commerce</option>
                      <option value="TradeIndia">TradeIndia B2B Commerce</option>
                      <option value="Meesho">Meesho Social Commerce</option>
                      <option value="AJIO">AJIO Fashion Commerce</option>
                      <option value="Myntra">Myntra Fashion Commerce</option>
                      <option value="AliExpress">AliExpress Market</option>
                      <option value="Global">Global Multi-Platform Search</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Brand / Manufacturer Context
                    </label>
                    <input
                      type="text"
                      value={brand}
                      onChange={e => setBrand(e.target.value)}
                      placeholder="e.g. Apple, Sony, Nothing, Nike"
                      className="w-full p-2.5 border border-border rounded-lg text-sm bg-surface"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                      Product / Model / SKU
                    </label>
                    <input
                      type="text"
                      value={product}
                      onChange={e => setProduct(e.target.value)}
                      placeholder="e.g. WH-1000XM5 or Phone 2a"
                      className="w-full p-2.5 border border-border rounded-lg text-sm bg-surface"
                    />
                  </div>
                </div>

                {/* Known Seller Optional */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Target Seller / Storefront Handle (Optional)
                  </label>
                  <input
                    type="text"
                    value={seller}
                    onChange={e => setSeller(e.target.value)}
                    placeholder="e.g. TechDeals Global Outlet"
                    className="w-full p-2.5 border border-border rounded-lg text-sm bg-surface"
                  />
                </div>
              </div>
            )}

            {/* TAB 2: MISSION TYPE & OBJECTIVES */}
            {activeTab === 'mission' && (
              <div className="space-y-6 animate-fadeIn">
                {/* Mission Type Selection */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                    Select Autonomous Mission Type
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {MISSION_TYPES.map(mt => {
                      const isSelected = investigationType === mt.id;
                      return (
                        <div
                          key={mt.id}
                          onClick={() => setInvestigationType(mt.id)}
                          className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                            isSelected
                              ? 'border-primary bg-primary/5 ring-1 ring-primary shadow-sm'
                              : 'border-border bg-surface hover:bg-slate-50'
                          }`}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <h4 className="text-sm font-bold text-slate-900">{mt.title}</h4>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                              {mt.badge}
                            </span>
                          </div>
                          <p className="text-xs text-muted mb-3 line-clamp-2">{mt.description}</p>
                          <div className="flex items-center gap-4 text-[10px] text-slate-500 font-mono pt-2 border-t border-border/60">
                            <span className="flex items-center gap-1"><Bot className="h-3 w-3 text-primary" /> {mt.agentsCount} Swarm Agents</span>
                            <span className="flex items-center gap-1"><Clock className="h-3 w-3 text-slate-400" /> Est. {mt.runtime}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Structured Objectives Checklist */}
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Structured Intelligence Objectives ({selectedObjectives.length} Selected)
                    </label>
                    <button
                      type="button"
                      onClick={() => setSelectedObjectives(MISSION_OBJECTIVES.map(o => o.id))}
                      className="text-xs text-primary hover:underline font-medium"
                    >
                      Select All
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {MISSION_OBJECTIVES.map(obj => {
                      const isChecked = selectedObjectives.includes(obj.id) && !obj.comingSoon;
                      const isDisabled = obj.comingSoon;
                      return (
                        <div
                          key={obj.id}
                          onClick={() => !isDisabled && toggleObjective(obj.id)}
                          className={`flex items-center justify-between p-2.5 rounded-lg border text-xs transition-all ${
                            isDisabled
                              ? 'border-border bg-slate-100/60 text-slate-400 cursor-not-allowed opacity-75'
                              : isChecked
                              ? 'border-emerald-300 bg-emerald-50/50 text-slate-900 font-medium cursor-pointer'
                              : 'border-border bg-surface text-slate-600 hover:bg-slate-50 cursor-pointer'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`h-4 w-4 rounded flex items-center justify-center border transition-all ${
                              isChecked ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 bg-white'
                            }`}>
                              {isChecked && <CheckCircle2 className="h-3 w-3" />}
                            </div>
                            <span>{obj.label}</span>
                          </div>
                          {isDisabled && (
                            <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-amber-100 text-amber-800 border border-amber-300 shrink-0">
                              Coming Soon
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: SWARM STRATEGY */}
            {activeTab === 'strategy' && (
              <div className="space-y-6 animate-fadeIn">
                {/* AI Planning Strategy Selector */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                    AI Swarm Planning Strategy
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {PLANNING_STRATEGIES.map(strat => {
                      const isSelected = plannerStrategy === strat.id;
                      const IconComp = strat.icon;
                      return (
                        <div
                          key={strat.id}
                          onClick={() => setPlannerStrategy(strat.id)}
                          className={`p-4 rounded-xl border cursor-pointer transition-all ${
                            isSelected
                              ? 'border-primary bg-primary/5 ring-1 ring-primary shadow-sm'
                              : 'border-border bg-surface hover:bg-slate-50'
                          }`}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <div className="flex items-center gap-2">
                              <IconComp className="h-4 w-4 text-primary shrink-0" />
                              <h4 className="text-sm font-bold text-slate-900">{strat.title}</h4>
                            </div>
                            <span className="text-xs font-mono font-semibold text-primary">{strat.runtime}</span>
                          </div>
                          <p className="text-xs text-muted mb-3">{strat.desc}</p>
                          <div className="flex items-center gap-4 text-[10px] font-mono text-slate-500 pt-2 border-t border-border/60">
                            <span className="flex items-center gap-1"><Bot className="h-3 w-3 text-slate-400" /> {strat.agents} Swarm Agents</span>
                            <span className="flex items-center gap-1"><Globe className="h-3 w-3 text-slate-400" /> {strat.providers} Providers</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Priority Selector */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Swarm Priority Level
                  </label>
                  <div className="grid grid-cols-4 gap-3">
                    {(['low', 'medium', 'high', 'critical'] as const).map(p => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setPriority(p)}
                        className={`py-2 px-3 rounded-lg border text-xs font-bold uppercase tracking-wider transition-all ${
                          priority === p
                            ? p === 'critical' ? 'bg-red-600 border-red-600 text-white'
                              : p === 'high' ? 'bg-amber-500 border-amber-500 text-white'
                              : 'bg-primary border-primary text-white'
                            : 'bg-surface border-border text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Participating Swarm Grid */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Deployed Autonomous Swarm Agents ({SWARM_AGENTS.length})
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {SWARM_AGENTS.map(agent => {
                      const AgentIcon = agent.icon;
                      return (
                        <div key={agent.name} className="p-2 rounded-lg border border-border bg-slate-50/70 flex items-center gap-2">
                          <div className="h-6 w-6 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
                            <AgentIcon className="h-3.5 w-3.5" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-xs font-bold text-slate-900 truncate">{agent.name}</p>
                            <p className="text-[9px] text-muted truncate">{agent.role}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* ADVANCED OPTIONS COLLAPSIBLE */}
            <div className="pt-4 border-t border-border">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center justify-between w-full text-xs font-bold text-slate-700 uppercase tracking-wider py-1 hover:text-primary transition-colors"
              >
                <span className="flex items-center gap-2"><Sliders className="h-4 w-4" /> Advanced Swarm Parameters</span>
                {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>

              {showAdvanced && (
                <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-border space-y-4 text-xs animate-fadeIn">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Target Region</label>
                      <select
                        value={advancedOptions.region}
                        onChange={e => setAdvancedOptions(prev => ({ ...prev, region: e.target.value }))}
                        className="w-full p-2 rounded border border-border bg-surface"
                      >
                        <option value="Global">Global (All Regions)</option>
                        <option value="US">North America (US / CA)</option>
                        <option value="EU">Europe (EU / UK)</option>
                        <option value="IN">Asia Pacific (IN / SG)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Search Depth</label>
                      <select
                        value={advancedOptions.searchDepth}
                        onChange={e => setAdvancedOptions(prev => ({ ...prev, searchDepth: e.target.value }))}
                        className="w-full p-2 rounded border border-border bg-surface"
                      >
                        <option value="Standard">Standard Multi-Agent</option>
                        <option value="Deep">Deep Parallel Fan-Out</option>
                        <option value="Exhaustive">Exhaustive Threat Sweep</option>
                      </select>
                    </div>

                    <div>
                      <label className="block font-semibold text-slate-700 mb-1">Max Retrieval Providers</label>
                      <input
                        type="number"
                        min={1}
                        max={6}
                        value={advancedOptions.maxProviders}
                        onChange={e => setAdvancedOptions(prev => ({ ...prev, maxProviders: parseInt(e.target.value) || 6 }))}
                        className="w-full p-2 rounded border border-border bg-surface"
                      />
                    </div>
                  </div>

                  <div className="flex gap-6 pt-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={advancedOptions.enableMemory}
                        onChange={e => setAdvancedOptions(prev => ({ ...prev, enableMemory: e.target.checked }))}
                        className="rounded border-slate-300 text-primary"
                      />
                      <span>Chroma Vector Episode Memory</span>
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={advancedOptions.enableGraph}
                        onChange={e => setAdvancedOptions(prev => ({ ...prev, enableGraph: e.target.checked }))}
                        className="rounded border-slate-300 text-primary"
                      />
                      <span>Neo4j Knowledge Graph Entity Resolution</span>
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* Analyst Directives Notes */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Analyst Intelligence Directives & Notes
              </label>
              <textarea
                value={notes}
                onChange={e => setNotes(e.target.value)}
                rows={2}
                placeholder="Provide specific instructions or threat hypotheses for the autonomous planner agent..."
                className="w-full p-2.5 border border-border rounded-xl text-xs bg-surface"
              />
            </div>

          </div>

          {/* Modal Footer / Live Summary */}
          <div className="p-6 border-t border-border bg-slate-50 flex flex-col md:flex-row gap-4 justify-between items-center shrink-0">
            {/* Live Summary Chips */}
            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Target:</span>
                <span className="font-bold text-slate-900 truncate max-w-[140px]">
                  {targetValue || brand || 'Not set'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Strategy:</span>
                <span className="font-bold text-primary">{selectedStrategyInfo.title}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">Est. Time:</span>
                <span className="font-bold text-emerald-600">{selectedStrategyInfo.runtime}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 w-full md:w-auto justify-end">
              <Button variant="outline" type="button" onClick={onClose}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!isValid || isPending}
                className="bg-gradient-to-r from-primary to-blue-700 hover:from-primary-dark hover:to-blue-800 text-white font-bold px-6 shadow-md"
              >
                {isPending ? (
                  <span className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Deploying Swarm...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    🚀 Launch Autonomous Mission <ArrowRight className="h-4 w-4" />
                  </span>
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

function TargetStepIcon({ isValid }: { isValid: boolean }) {
  if (isValid) {
    return <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />;
  }
  return <Search className="h-4 w-4 shrink-0" />;
}
