/**
 * NotificationToastContainer.tsx — Phase 5: Enterprise Toast Notifications System
 * Renders high-priority SOC alert toasts in the bottom-right viewport.
 */
import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert, X, Info } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  description?: string;
  timestamp: string;
}

interface NotificationToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export function NotificationToastContainer({ toasts, onDismiss }: NotificationToastContainerProps) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => {
        const isError = toast.type === 'error';
        const isWarning = toast.type === 'warning';
        const isSuccess = toast.type === 'success';

        const styleClass = isError
          ? 'bg-red-900/90 text-white border-red-700'
          : isWarning
          ? 'bg-amber-900/90 text-white border-amber-700'
          : isSuccess
          ? 'bg-slate-900/90 text-white border-emerald-500/50'
          : 'bg-slate-900/90 text-white border-slate-700';

        const icon = isError ? (
          <ShieldAlert className="h-5 w-5 text-red-400 shrink-0" />
        ) : isWarning ? (
          <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
        ) : isSuccess ? (
          <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
        ) : (
          <Info className="h-5 w-5 text-blue-400 shrink-0" />
        );

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto p-4 rounded-xl border shadow-2xl backdrop-blur-md flex items-start gap-3 transition-all animate-in slide-in-from-right duration-200 ${styleClass}`}
          >
            {icon}
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold truncate">{toast.title}</div>
              {toast.description && <div className="text-[11px] text-slate-300 mt-0.5 leading-snug">{toast.description}</div>}
              <div className="text-[9px] text-slate-400 mt-1">{toast.timestamp}</div>
            </div>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-slate-400 hover:text-white p-0.5 rounded transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
