import { useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { DEFAULT_FEATURE_FLAGS, type FeatureFlag } from '../config/featureFlags';

export function useFeatureFlag(flagName: FeatureFlag): boolean {
  const context = useContext(AppContext);
  // Optional chaining to be safe against Context missing or initialization issues
  const featureFlags = context?.featureFlags || DEFAULT_FEATURE_FLAGS;
  return featureFlags[flagName] ?? DEFAULT_FEATURE_FLAGS[flagName];
}
