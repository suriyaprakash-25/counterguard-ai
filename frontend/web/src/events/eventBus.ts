import { InvestigationCompletedPayload } from './investigation.events';
import { AlertCreatedPayload } from './alert.events';
import { RealtimeEvent } from '../shared/realtime/events';

export interface AppEventMap {
  'investigation:created': { id: string };
  'investigation:updated': { id: string };
  'investigation:completed': InvestigationCompletedPayload;
  'investigation:consensus_reached': { id: string };
  'alert:created': AlertCreatedPayload;
  'alert:acknowledged': { alertId: string };
  'alert:dismissed': { alertId: string };
  // Realtime Streaming Events
  'stream:event': RealtimeEvent;
  // Auth Events
  'auth:forced_logout': void;
}

type EventCallback<K extends keyof AppEventMap> = (payload: AppEventMap[K]) => void;

class EventBus {
  private listeners: Map<keyof AppEventMap, EventCallback<any>[]>;

  constructor() {
    this.listeners = new Map();
  }

  public subscribe<K extends keyof AppEventMap>(event: K, callback: EventCallback<K>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }

    this.listeners.get(event)!.push(callback);

    return () => this.unsubscribe(event, callback);
  }

  public unsubscribe<K extends keyof AppEventMap>(event: K, callback: EventCallback<K>): void {
    if (!this.listeners.has(event)) return;

    const callbacks = this.listeners.get(event)!.filter(cb => cb !== callback);
    if (callbacks.length === 0) {
      this.listeners.delete(event);
    } else {
      this.listeners.set(event, callbacks);
    }
  }

  public publish<K extends keyof AppEventMap>(event: K, payload: AppEventMap[K]): void {
    if (!this.listeners.has(event)) return;

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

export const eventBus = new EventBus();
