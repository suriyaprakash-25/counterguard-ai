import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/common/Button';
import { ShieldAlert } from 'lucide-react';

export function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
        <div className="mx-auto w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
          <ShieldAlert className="h-8 w-8 text-red-500" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Access Denied</h1>
        <p className="text-slate-600 mb-8">
          You do not have the required permissions to view this page. If you believe this is an error, please contact your administrator.
        </p>
        <Button onClick={() => navigate('/')} className="w-full">
          Return to Dashboard
        </Button>
      </div>
    </div>
  );
}
