import { useEffect, useState, useRef } from 'react';
import { WebSocketTransport } from './websocket';
import { SSETransport } from './sse';
import type { RealtimeTransport } from './transport';
import { ReconnectManager } from './reconnect';
import { eventBus } from '../../events/eventBus';
import type { RealtimeEvent } from './events';

const PROVIDER = import.meta.env.VITE_REALTIME_PROVIDER || 'sse'; // fallback to sse
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useRealtime(investigationId: string) {
  const [isConnected, setIsConnected] = useState(false);
  const transportRef = useRef<RealtimeTransport | null>(null);
  const reconnectRef = useRef<ReconnectManager | null>(null);

  useEffect(() => {
    if (!investigationId) return;

    if (!reconnectRef.current) {
      reconnectRef.current = new ReconnectManager();
    }

    if (!transportRef.current) {
      transportRef.current = PROVIDER === 'websocket' ? new WebSocketTransport() : new SSETransport();
    }

    const transport = transportRef.current;
    const reconnectManager = reconnectRef.current;

    const connect = () => {
      const url = PROVIDER === 'websocket'
        ? `${API_BASE.replace('http', 'ws')}/api/v1/investigations/${investigationId}/stream`
        : `${API_BASE}/api/v1/investigations/${investigationId}/stream`;

      transport.connect(url, {
        onOpen: () => {
          setIsConnected(true);
          reconnectManager.reset();
          console.log(`[Realtime] Connected to stream for ${investigationId} via ${PROVIDER}`);
        },
        onMessage: (data: RealtimeEvent) => {
          // Publish the parsed event to the typed event bus
          eventBus.publish('stream:event', data);
        },
        onClose: () => {
          setIsConnected(false);
          reconnectManager.scheduleReconnect(connect);
        },
        onError: (err) => {
          console.error(`[Realtime] Error`, err);
        }
      });
    };

    connect();

    return () => {
      reconnectManager.stop();
      transport.disconnect();
      setIsConnected(false);
    };
  }, [investigationId]);

  return { isConnected };
}
