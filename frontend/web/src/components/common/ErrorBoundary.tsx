/**
 * ErrorBoundary.tsx — Phase 2: React Component Production Error Boundary
 * Catches unhandled UI rendering exceptions and presents a clean recovery interface.
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary] Caught unhandled React error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[50vh] flex flex-col items-center justify-center p-6 text-center space-y-4 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 m-4">
          <div className="p-3 rounded-full bg-red-100 dark:bg-red-950 text-red-600 dark:text-red-400">
            <ShieldAlert className="h-8 w-8" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Unexpected Component Error Caught</h2>
          <p className="text-xs text-slate-500 max-w-md">
            {this.state.error?.message || 'CounterGuard encountered an unexpected UI rendering exception.'}
          </p>
          <button
            onClick={this.handleReset}
            className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Reload Application Workspace
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
