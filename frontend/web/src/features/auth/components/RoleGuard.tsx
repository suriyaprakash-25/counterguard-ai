import { ReactNode } from 'react';
import { useAuth } from '../AuthContext';
import { UserRole } from '../models';
import { hasMinimumRole } from '../permissions';

interface RoleGuardProps {
  children: ReactNode;
  require: UserRole;
  fallback?: ReactNode;
}

export function RoleGuard({ children, require, fallback = null }: RoleGuardProps) {
  const { user } = useAuth();

  if (hasMinimumRole(user, require)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}
