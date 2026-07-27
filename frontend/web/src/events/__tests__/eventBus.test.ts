import { describe, it, expect, vi, beforeEach } from 'vitest';
import { eventBus } from '../eventBus';

describe('Event Bus', () => {
  beforeEach(() => {
    eventBus.clearAll();
    vi.useFakeTimers();
  });

  it('subscribes and receives events', () => {
    const handler = vi.fn();
    eventBus.subscribe('test:event', handler);

    eventBus.publish('test:event', { foo: 'bar' });
    vi.runAllTimers();

    expect(handler).toHaveBeenCalledWith({ foo: 'bar' });
  });

  it('unsubscribes successfully via returned function', () => {
    const handler = vi.fn();
    const unsubscribe = eventBus.subscribe('test:event', handler);

    unsubscribe();
    eventBus.publish('test:event', { foo: 'bar' });
    vi.runAllTimers();

    expect(handler).not.toHaveBeenCalled();
  });

  it('handles multiple subscribers to same event', () => {
    const handler1 = vi.fn();
    const handler2 = vi.fn();

    eventBus.subscribe('test:multi', handler1);
    eventBus.subscribe('test:multi', handler2);

    eventBus.publish('test:multi', 'payload');
    vi.runAllTimers();

    expect(handler1).toHaveBeenCalledWith('payload');
    expect(handler2).toHaveBeenCalledWith('payload');
  });
});
