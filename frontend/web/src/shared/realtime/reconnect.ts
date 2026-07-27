export interface ReconnectConfig {
  maxRetries?: number;
  initialDelayMs?: number;
  maxDelayMs?: number;
  backoffFactor?: number;
}

export class ReconnectManager {
  private retries = 0;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private readonly maxRetries: number;
  private readonly initialDelayMs: number;
  private readonly maxDelayMs: number;
  private readonly backoffFactor: number;

  constructor(config?: ReconnectConfig) {
    this.maxRetries = config?.maxRetries ?? 10;
    this.initialDelayMs = config?.initialDelayMs ?? 1000;
    this.maxDelayMs = config?.maxDelayMs ?? 30000;
    this.backoffFactor = config?.backoffFactor ?? 1.5;
  }

  public scheduleReconnect(callback: () => void): void {
    if (this.retries >= this.maxRetries) {
      console.warn('[ReconnectManager] Max retries reached.');
      return;
    }

    if (this.timer) {
      clearTimeout(this.timer);
    }

    const delay = Math.min(
      this.initialDelayMs * Math.pow(this.backoffFactor, this.retries),
      this.maxDelayMs
    );

    console.log(`[ReconnectManager] Scheduling reconnect attempt ${this.retries + 1} in ${delay}ms`);

    this.timer = setTimeout(() => {
      this.retries++;
      callback();
    }, delay);
  }

  public reset(): void {
    this.retries = 0;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }

  public stop(): void {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}
