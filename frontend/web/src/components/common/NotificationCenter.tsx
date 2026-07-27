import { useState } from "react";
import { Bell, Bot, ShieldAlert, Zap, Server } from "lucide-react";
import { Badge } from "./Badge";

export interface NotificationItem {
  id: string;
  title: string;
  description: string;
  type: "alert" | "system" | "agent" | "graph";
  timestamp: string;
  read: boolean;
}

export function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);

  // Mock notifications for UI demonstration
  const [notifications] = useState<NotificationItem[]>([
    { id: "1", title: "New Fraud Ring Detected", description: "Graph Intelligence identified a new 45-node cluster.", type: "graph", timestamp: new Date().toISOString(), read: false },
    { id: "2", title: "Planner Scheduled Job", description: "Marketplace sweep started for 3 ASINs.", type: "agent", timestamp: new Date(Date.now() - 3600000).toISOString(), read: false },
    { id: "3", title: "Critical Alert: IP Violation", description: "Apple AirPods counterfeits found on Temu.", type: "alert", timestamp: new Date(Date.now() - 7200000).toISOString(), read: true },
    { id: "4", title: "Memory Engine Synced", description: "1,200 new embeddings generated.", type: "system", timestamp: new Date(Date.now() - 86400000).toISOString(), read: true },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const getIcon = (type: string) => {
    switch(type) {
      case 'alert': return <ShieldAlert className="h-4 w-4 text-danger" />;
      case 'agent': return <Bot className="h-4 w-4 text-primary" />;
      case 'graph': return <Zap className="h-4 w-4 text-warning" />;
      default: return <Server className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-slate-500 hover:text-slate-900 transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-full"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-danger ring-2 ring-white" />
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-border z-50 overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-border bg-slate-50">
              <h3 className="font-semibold text-slate-900">Notifications</h3>
              <Badge variant="outline">{unreadCount} New</Badge>
            </div>
            <div className="max-h-[400px] overflow-y-auto">
              {notifications.map(notif => (
                <div key={notif.id} className={`p-4 border-b border-border last:border-b-0 hover:bg-slate-50 transition-colors cursor-pointer ${!notif.read ? 'bg-blue-50/30' : ''}`}>
                  <div className="flex gap-3">
                    <div className="mt-0.5">{getIcon(notif.type)}</div>
                    <div>
                      <p className={`text-sm font-medium ${!notif.read ? 'text-slate-900' : 'text-slate-700'}`}>{notif.title}</p>
                      <p className="text-xs text-slate-500 mt-1 line-clamp-2">{notif.description}</p>
                      <p className="text-[10px] text-muted mt-2">
                        {new Date(notif.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-3 border-t border-border bg-slate-50 text-center">
              <button className="text-sm text-primary font-medium hover:underline">View All Notifications</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
