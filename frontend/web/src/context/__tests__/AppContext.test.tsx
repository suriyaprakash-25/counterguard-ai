import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useFeatureFlag } from '../../hooks/useFeatureFlag';
import { AppProvider } from '../AppContext';
import type { ReactNode } from 'react';

describe('Application Context & Feature Flags', () => {
  it('provides default feature flags when context wraps hook', () => {
    const wrapper = ({ children }: { children: ReactNode }) => (
      <AppProvider>{children}</AppProvider>
    );

    const { result } = renderHook(() => useFeatureFlag('GRAPH_RAG_OVERLAY'), { wrapper });

    // GRAPH_RAG_OVERLAY defaults to true
    expect(result.current).toBe(true);
  });

  it('returns false for disabled flags', () => {
    const wrapper = ({ children }: { children: ReactNode }) => (
      <AppProvider>{children}</AppProvider>
    );

    const { result } = renderHook(() => useFeatureFlag('AI_CHAT_ASSISTANT'), { wrapper });

    // AI_CHAT_ASSISTANT defaults to false
    expect(result.current).toBe(false);
  });
});
