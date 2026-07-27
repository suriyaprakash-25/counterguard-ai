import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../AuthContext';
import { Button } from '../../../components/common/Button';
import { Shield } from 'lucide-react';
import { useForm as useReactHookForm } from 'react-hook-form';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [globalError, setGlobalError] = useState('');

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useReactHookForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    }
  });

  const from = location.state?.from?.pathname || '/dashboard';

  const onSubmit = async (data: LoginForm) => {
    setGlobalError('');
    try {
      await login(data);
      navigate(from, { replace: true });
    } catch (err: any) {
      setGlobalError(err.message || 'Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        <div className="bg-slate-900 p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 bg-blue-500 rounded-2xl flex items-center justify-center shadow-lg transform rotate-3">
              <Shield className="h-8 w-8 text-white -rotate-3" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">CounterGuard</h1>
          <p className="text-slate-400 mt-2 text-sm">Intelligence Platform</p>
        </div>

        <div className="p-8 pt-6">
          <h2 className="text-xl font-semibold text-slate-800 mb-6 text-center">Sign in to your account</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {globalError && (
              <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-100 text-center">
                {globalError}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email address</label>
              <input
                {...register('email')}
                type="email"
                placeholder="investigator@counterguard.ai"
                className={`w-full px-4 py-2.5 rounded-lg border bg-slate-50 focus:bg-white text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 ${errors.email ? 'border-red-300' : 'border-slate-200'}`}
              />
              {errors.email && <p className="text-red-500 text-xs mt-1.5">{errors.email.message}</p>}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium text-slate-700">Password</label>
                <a href="#" className="text-xs font-medium text-blue-600 hover:text-blue-500">Forgot password?</a>
              </div>
              <input
                {...register('password')}
                type="password"
                placeholder="••••••••"
                className={`w-full px-4 py-2.5 rounded-lg border bg-slate-50 focus:bg-white text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 ${errors.password ? 'border-red-300' : 'border-slate-200'}`}
              />
              {errors.password && <p className="text-red-500 text-xs mt-1.5">{errors.password.message}</p>}
            </div>

            <div className="flex items-center">
              <input
                {...register('rememberMe')}
                id="remember"
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-600 cursor-pointer"
              />
              <label htmlFor="remember" className="ml-2 block text-sm text-slate-600 cursor-pointer">
                Remember me for 30 days
              </label>
            </div>

            <Button
              type="submit"
              className="w-full h-11 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Authenticating...' : 'Sign In'}
            </Button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400">
            For demonstration purposes, any credentials will work if intercepted by MSW.
          </p>
        </div>
      </div>
    </div>
  );
}
