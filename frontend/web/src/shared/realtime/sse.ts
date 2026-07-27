import type { RealtimeTransport, RealtimeTransportCallbacks } from './transport';

export class SSETransport implements RealtimeTransport {
  private eventSource: EventSource | null = null;

  connect(url: string, callbacks: RealtimeTransportCallbacks): void {
    if (this.eventSource) {
      this.disconnect();
    }

    try {
      this.eventSource = new EventSource(url, { withCredentials: true });

      this.eventSource.onopen = () => {
        callbacks.onOpen();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          callbacks.onMessage(data);
        } catch (err) {
          console.error('[SSE] Failed to parse message', err);
        }
      };

      this.eventSource.onerror = (error) => {
        // EventSource will automatically try to reconnect.
        // We notify onError, but let EventSource handle its own backoff,
        // unless it's in a CLOSED state.
        callbacks.onError(error);
        if (this.eventSource?.readyState === EventSource.CLOSED) {
          callbacks.onClose(error);
        }
      };
    } catch (err) {
      callbacks.onError(err);
    }
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
