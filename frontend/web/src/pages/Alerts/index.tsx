import { useState } from "react";
import { PageHeader } from "../../components/common/PageHeader";
import { SplitView } from "../../components/common/SplitView";
import { AlertListWidget, AlertDetailsWidget } from "./widgets/Widgets";

export default function AlertsCenter() {
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] pb-4">
      <div className="shrink-0">
        <PageHeader
          title="Alerts Center"
          description="Review high-priority intelligence alerts and escalate critical fraud cases."
        />
      </div>

      <div className="flex-1 min-h-0 mt-4">
        <SplitView
          masterWidth="w-full md:w-[450px]"
          master={<AlertListWidget selectedId={selectedAlertId} onSelect={setSelectedAlertId} />}
          detail={<AlertDetailsWidget alertId={selectedAlertId} />}
          showDetailOnMobile={!!selectedAlertId} // Very simple mobile handling
        />
      </div>
    </div>
  );
}
