import { useState } from 'react';
import { Button } from '../../components/common/Button';
import { useCreateInvestigation } from '../../hooks/useInvestigations';
import { useNavigate } from 'react-router-dom';

interface CreateInvestigationDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateInvestigationDialog({ isOpen, onClose }: CreateInvestigationDialogProps) {
  const navigate = useNavigate();
  const { mutate: createInvestigation, isPending } = useCreateInvestigation();

  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    marketplace: 'Amazon',
    product: '',
    seller: '',
    plannerPriority: 'medium',
    notes: ''
  });

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createInvestigation(formData, {
      onSuccess: (data) => {
        onClose();
        navigate(`/investigations/${data.id}`);
      },
      onError: (err) => {
        console.error('Failed to create investigation:', err);
      }
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-surface rounded-xl shadow-xl w-full max-w-2xl border border-border mt-10 mb-10 overflow-hidden flex flex-col">
        <div className="p-6 border-b border-border bg-slate-50 flex justify-between items-center shrink-0">
          <div>
            <h2 className="text-xl font-bold text-slate-900">New Autonomous Investigation</h2>
            <p className="text-sm text-muted mt-1">Configure parameters for the LangGraph agent swarm.</p>
          </div>
          <button onClick={onClose} className="text-muted hover:text-slate-900">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Investigation Name</label>
              <input required name="name" value={formData.name} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent" placeholder="e.g. Suspicious iPhone 15 Pro Batch" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Brand Context</label>
                <input required name="brand" value={formData.brand} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent" placeholder="e.g. Apple" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Target Marketplace</label>
                <select name="marketplace" value={formData.marketplace} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent">
                  <option value="Amazon">Amazon</option>
                  <option value="eBay">eBay</option>
                  <option value="Walmart">Walmart</option>
                  <option value="AliExpress">AliExpress</option>
                  <option value="Global">Global Search</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Product Details</label>
                <input name="product" value={formData.product} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent" placeholder="Specific model or SKU" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Known Seller (Optional)</label>
                <input name="seller" value={formData.seller} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent" placeholder="Storefront URL or Name" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Planner Priority</label>
              <select name="plannerPriority" value={formData.plannerPriority} onChange={handleChange} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent">
                <option value="low">Low - Background Analysis</option>
                <option value="medium">Medium - Standard Priority</option>
                <option value="high">High - Expedited Execution</option>
                <option value="critical">Critical - Immediate Swarm Deployment</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Investigation Directives & Notes</label>
              <textarea name="notes" value={formData.notes} onChange={handleChange} rows={4} className="w-full p-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary focus:border-transparent" placeholder="Provide specific instructions to the planner agent..." />
            </div>
          </div>

          <div className="p-6 border-t border-border bg-slate-50 flex justify-end gap-3 shrink-0">
            <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Deploying Swarm...' : 'Launch Investigation'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
