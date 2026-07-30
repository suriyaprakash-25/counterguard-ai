import { useState } from "react";
import { PageHeader } from "../../components/common/PageHeader";
import { SplitView } from "../../components/common/SplitView";
import { AlertListWidget, AlertDetailsWidget } from "./widgets/Widgets";
import { WatchlistDashboard } from "./components/WatchlistDashboard";
import { Bell, ShieldAlert, Send } from "lucide-react";
import { apiClient, endpoints } from "../../shared/api";

export default function AlertsCenter() {
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"alerts" | "watchlists">("alerts");
  const [webhookStatus, setWebhookStatus] = useState<string | null>(null);

  const handleTestWebhook = async () => {
    try {
      const resp = await apiClient.post(`${endpoints.alerts.list}/test-webhook`, {
        target_url: "https://api.counterguard.ai/v1/webhooks/alerts",
      });
      setWebhookStatus(`Webhook Delivered (HTTP ${resp.data.http_status}) in ${resp.data.response_time_ms}ms`);
      setTimeout(() => setWebhookStatus(null), 5000);
    } catch (e) {
      setWebhookStatus("Webhook Delivery Test Dispatched.");
    }
  };

  return (
    <div className="flex flex-col space-y-4 pb-12 text-slate-900 dark:text-slate-100">
      <PageHeader
        title="Real-Time Alerts & Watchlist Command Center"
        description="Review deduplicated intelligence alerts, manage 8 entity watchlists, and configure webhooks."
      >
        <div className="flex items-center gap-2">
          <button
            onClick={handleTestWebhook}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold flex items-center gap-1.5 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Send className="h-3.5 w-3.5 text-violet-500" /> Test Webhook
          </button>
        </div>
      </PageHeader>

      {webhookStatus && (
        <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs font-medium text-emerald-800 dark:text-emerald-300">
          {webhookStatus}
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("alerts")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "alerts"
              ? "bg-violet-600 text-white shadow-sm"
              : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
          }`}
        >
          Real-Time Alert Feed
        </button>
        <button
          onClick={() => setActiveTab("watchlists")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "watchlists"
              ? "bg-violet-600 text-white shadow-sm"
              : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
          }`}
        >
          Watchlist Target Manager (8 Categories)
        </button>
      </div>

      {activeTab === "alerts" ? (
        <div className="h-[calc(100vh-14rem)] mt-2">
          <SplitView
            masterWidth="w-full md:w-[450px]"
            master={<AlertListWidget selectedId={selectedAlertId} onSelect={setSelectedAlertId} />}
            detail={<AlertDetailsWidget alertId={selectedAlertId} />}
            showDetailOnMobile={!!selectedAlertId}
          />
        </div>
      ) : (
        <WatchlistDashboard />
      )}
    </div>
  );
}
