import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[CounterGuard Extension ErrorBoundary]", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-slate-900 text-white rounded-xl border border-red-500/30 text-center space-y-3">
          <h3 className="text-sm font-bold text-red-400">Extension Error Encountered</h3>
          <p className="text-xs text-slate-300 font-mono break-all">
            {this.state.error?.message || "An unexpected error occurred in CounterGuard extension."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded transition-colors"
          >
            Reset Extension State
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
