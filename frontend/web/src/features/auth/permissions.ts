import { User, UserRole } from './models';

const roleHierarchy: Record<UserRole, number> = {
  Administrator: 40,
  Investigator: 30,
  Analyst: 20,
  Viewer: 10,
};

export const hasMinimumRole = (user: User | null, role: UserRole): boolean => {
  if (!user) return false;
  return roleHierarchy[user.role] >= roleHierarchy[role];
};

export const canCreateInvestigation = (user: User | null): boolean => {
  return hasMinimumRole(user, 'Investigator');
};

export const canDeleteInvestigation = (user: User | null): boolean => {
  return hasMinimumRole(user, 'Administrator');
};

export const canCancelInvestigation = (user: User | null): boolean => {
  return hasMinimumRole(user, 'Investigator');
};

export const canViewAnalytics = (user: User | null): boolean => {
  return hasMinimumRole(user, 'Analyst');
};

export const canManageSettings = (user: User | null): boolean => {
  return hasMinimumRole(user, 'Administrator');
};
