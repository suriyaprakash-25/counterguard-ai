export interface RealtimeTransportCallbacks {
  onMessage: (data: any) => void;
  onOpen: () => void;
  onClose: (event?: any) => void;
  onError: (error: any) => void;
}

export interface RealtimeTransport {
  connect(url: string, callbacks: RealtimeTransportCallbacks): void;
  disconnect(): void;
}
