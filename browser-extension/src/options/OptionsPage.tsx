import { useState, useEffect } from "react";
import {
  Shield,
  Server,
  Bell,
  Sun,
  Moon,
  Zap,
  CheckCircle2,
  AlertCircle,
  Save,
  RotateCcw,
  ExternalLink,
  Globe,
  Database
} from "lucide-react";
import { useChromeStorage } from "../hooks/useChromeStorage";
import { BackendApiClient } from "../api/client";
import { DEFAULT_SETTINGS } from "../services/storage.service";

export function OptionsPage() {
  const { settings, updateSettings, loading } = useChromeStorage();

  const [form, setForm] = useState(settings);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (!loading) {
      setForm(settings);
    }
  }, [loading, settings]);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    const result = await BackendApiClient.checkHealth(form.backendUrl);
    setTesting(false);

    if (result.isOnline) {
      setTestResult({
        success: true,
        message: `Connected successfully to FastAPI ${result.details?.app || "CounterGuard Backend"} (v${result.details?.version || "1.0.0"})`,
      });
    } else {
      setTestResult({
        success: false,
        message: `Failed to connect to FastAPI server at ${form.backendUrl}. Ensure uvicorn server is running on port 8000.`,
      });
    }
  };

  const handleSave = async () => {
    const success = await updateSettings(form);
    if (success) {
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }
  };

  const handleReset = () => {
    setForm(DEFAULT_SETTINGS);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white font-mono">
        Loading extension settings...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400 shadow-xl shadow-purple-900/20">
              <Shield className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                CounterGuard Extension Settings
                <span className="text-xs bg-purple-950 text-purple-300 font-mono px-2 py-0.5 rounded border border-purple-800">
                  Manifest V3
                </span>
              </h1>
              <p className="text-xs text-slate-400 font-mono">
                Enterprise Brand Protection & Threat Intelligence Configuration
              </p>
            </div>
          </div>

          <a
            href="http://localhost:5173"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-purple-400 transition-colors"
          >
            Launch Command Center <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </header>

        {/* Form Container */}
        <div className="space-y-6">
          {/* SECTION 1: Backend API Configuration */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <Server className="h-4 w-4 text-purple-400" />
              <span>FastAPI Backend Server URL</span>
            </div>

            <p className="text-xs text-slate-400">
              Specify the base URL for the CounterGuard FastAPI intelligence backend server.
            </p>

            <div className="flex gap-3">
              <input
                type="text"
                value={form.backendUrl}
                onChange={(e) => setForm({ ...form, backendUrl: e.target.value })}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs font-mono text-white outline-none focus:border-purple-500 transition-colors"
                placeholder="http://localhost:8000"
              />
              <button
                onClick={handleTestConnection}
                disabled={testing}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-xs font-bold text-purple-300 border border-slate-700 transition-colors flex items-center gap-1.5"
              >
                {testing ? "Testing..." : "Test Connection"}
              </button>
            </div>

            {testResult && (
              <div
                className={`p-3 rounded-xl border text-xs font-mono flex items-start gap-2 ${
                  testResult.success
                    ? "bg-emerald-950/40 border-emerald-800 text-emerald-300"
                    : "bg-red-950/40 border-red-800 text-red-300"
                }`}
              >
                {testResult.success ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                ) : (
                  <AlertCircle className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
                )}
                <span>{testResult.message}</span>
              </div>
            )}
          </div>

          {/* SECTION 2: Automated Threat Analysis */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2 text-sm font-bold text-white">
                  <Zap className="h-4 w-4 text-purple-400" />
                  <span>Automatic Page Analysis</span>
                </div>
                <p className="text-xs text-slate-400">
                  Automatically inspect active e-commerce marketplace tabs for counterfeit risk on navigation.
                </p>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.autoAnalyze}
                  onChange={(e) => setForm({ ...form, autoAnalyze: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600" />
              </label>
            </div>
          </div>

          {/* SECTION 3: Desktop Notifications */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2 text-sm font-bold text-white">
                  <Bell className="h-4 w-4 text-purple-400" />
                  <span>Threat Alert Notifications</span>
                </div>
                <p className="text-xs text-slate-400">
                  Display Chrome desktop toast notifications when high-severity counterfeit threats are detected.
                </p>
              </div>

              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.notifications}
                  onChange={(e) => setForm({ ...form, notifications: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600" />
              </label>
            </div>
          </div>

          {/* SECTION 4: Theme Mode Configuration */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2 text-sm font-bold text-white">
                <Moon className="h-4 w-4 text-purple-400" />
                <span>Extension Appearance & Theme</span>
              </div>
              <p className="text-xs text-slate-400">
                Choose visual mode for popup and options UI elements.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-2">
              <button
                type="button"
                onClick={() => setForm({ ...form, theme: "dark", lightMode: false })}
                className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-2 transition-all ${
                  form.theme === "dark"
                    ? "bg-purple-950/60 border-purple-500 text-purple-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                <Moon className="h-4 w-4" />
                <span>Dark Mode</span>
              </button>

              <button
                type="button"
                onClick={() => setForm({ ...form, theme: "light", lightMode: true })}
                className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-2 transition-all ${
                  form.theme === "light"
                    ? "bg-purple-950/60 border-purple-500 text-purple-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                <Sun className="h-4 w-4" />
                <span>Light Mode</span>
              </button>

              <button
                type="button"
                onClick={() => setForm({ ...form, theme: "system" })}
                className={`p-3 rounded-xl border text-xs font-bold flex flex-col items-center gap-2 transition-all ${
                  form.theme === "system"
                    ? "bg-purple-950/60 border-purple-500 text-purple-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                <Server className="h-4 w-4" />
                <span>System Preference</span>
              </button>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="pt-4 flex items-center justify-between border-t border-slate-800">
          <button
            onClick={handleReset}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Reset Defaults
          </button>

          <div className="flex items-center gap-3">
            {saveSuccess && (
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4" /> Settings Saved!
              </span>
            )}
            <button
              onClick={handleSave}
              className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-lg shadow-purple-900/30 transition-all flex items-center gap-2"
            >
              <Save className="h-4 w-4" /> Save Extension Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
