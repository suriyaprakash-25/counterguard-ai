import type { RealtimeTransport, RealtimeTransportCallbacks } from './transport';

export class WebSocketTransport implements RealtimeTransport {
  private ws: WebSocket | null = null;

  connect(url: string, callbacks: RealtimeTransportCallbacks): void {
    if (this.ws) {
      this.disconnect();
    }

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        callbacks.onOpen();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          callbacks.onMessage(data);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message', err);
        }
      };

      this.ws.onclose = (event) => {
        callbacks.onClose(event);
      };

      this.ws.onerror = (error) => {
        callbacks.onError(error);
      };
    } catch (err) {
      callbacks.onError(err);
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect loop from triggering if intentional
      this.ws.close();
      this.ws = null;
    }
  }
}
