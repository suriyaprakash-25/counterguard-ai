type EventCallback<T = any> = (payload: T) => void;

class EventBus {
  private listeners: Map<string, EventCallback[]>;

  constructor() {
    this.listeners = new Map();
  }

  public subscribe<T>(event: string, callback: EventCallback<T>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }

    this.listeners.get(event)!.push(callback);

    // Return unsubscribe function
    return () => this.unsubscribe(event, callback);
  }

  public unsubscribe<T>(event: string, callback: EventCallback<T>): void {
    if (!this.listeners.has(event)) return;

    const callbacks = this.listeners.get(event)!.filter(cb => cb !== callback);
    if (callbacks.length === 0) {
      this.listeners.delete(event);
    } else {
      this.listeners.set(event, callbacks);
    }
  }

  public publish<T>(event: string, payload: T): void {
    if (!this.listeners.has(event)) return;

    // Use setTimeout to ensure event handlers don't block the caller
    // and don't cause React rendering issues if they update state
    setTimeout(() => {
      this.listeners.get(event)!.forEach(callback => {
        try {
          callback(payload);
        } catch (error) {
          console.error(`[EventBus] Error in handler for ${event}:`, error);
        }
      });
    }, 0);
  }

  public clearAll(): void {
    this.listeners.clear();
  }
}

// Export singleton instance
export const eventBus = new EventBus();
