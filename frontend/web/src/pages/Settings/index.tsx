import { PageHeader } from "../../components/common/PageHeader";
import { SystemStatusWidget, ConfigurationWidget } from "./widgets/Widgets";

export default function PlatformSettings() {
  return (
    <div className="flex flex-col h-full pb-4">
      <div className="shrink-0 mb-6">
        <PageHeader
          title="Platform Settings"
          description="Configure CounterGuard, monitor system health, and manage integrations."
        />
      </div>

      <div className="flex-1 space-y-6">
        <SystemStatusWidget />
        <ConfigurationWidget />
      </div>
    </div>
  );
}
