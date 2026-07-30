/**
 * ErrorBoundary.tsx — React class component error boundary
 * Catches render-time errors in lazy-loaded popup tabs.
 * Provides a recovery UI with extension reload option.
 */

import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallbackLabel?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    // Log to console in dev; in prod Terser strips console.*
    console.error("[CounterGuard ErrorBoundary]", error, errorInfo);
  }

  handleReload = () => {
    // Try Chrome extension reload first; fall back to component reset
    if (typeof chrome !== "undefined" && chrome.runtime?.reload) {
      chrome.runtime.reload();
    } else {
      this.setState({ hasError: false, error: null, errorInfo: null });
    }
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        role="alert"
        aria-live="assertive"
        className="p-4 m-3 rounded-xl bg-red-950/60 border border-red-800/60 space-y-3 animate-fadeIn"
      >
        {/* Icon + Title */}
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-red-900/60 border border-red-700/60 flex items-center justify-center text-red-400 font-bold text-lg">
            ⚠
          </div>
          <div>
            <h2 className="text-xs font-bold text-red-300 font-mono">
              {this.props.fallbackLabel || "Component Error"}
            </h2>
            <p className="text-[9px] text-red-400/80 font-mono">
              An unexpected error occurred in the extension UI
            </p>
          </div>
        </div>

        {/* Error message */}
        {this.state.error && (
          <div className="bg-red-950 border border-red-900 rounded-lg px-3 py-2 font-mono text-[9px] text-red-300 break-all">
            {this.state.error.message}
          </div>
        )}

        {/* Recovery actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={this.handleReset}
            className="flex-1 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-[10px] font-mono transition-colors"
            aria-label="Retry rendering this component"
          >
            Try Again
          </button>
          <button
            onClick={this.handleReload}
            className="flex-1 py-1.5 px-3 rounded-lg bg-red-700 hover:bg-red-600 text-white font-bold text-[10px] font-mono transition-colors"
            aria-label="Reload the CounterGuard extension"
          >
            Reload Extension
          </button>
        </div>
      </div>
    );
  }
}
