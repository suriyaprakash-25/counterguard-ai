/**
 * performance.service.ts — Extension Performance Metrics Service
 * Wraps the native Performance API with structured timing capture.
 * Tracks key startup and analysis milestones for diagnostics.
 * In production, console output is stripped by Terser.
 */

export interface PerformanceMeasure {
  name: string;
  durationMs: number;
  startMs: number;
  endMs: number;
  timestamp: string;
}

export class PerformanceService {
  private static measures: PerformanceMeasure[] = [];
  private static readonly MAX_MEASURES = 50;

  /**
   * Mark a named performance point (start or end of a phase).
   */
  static mark(label: string): void {
    try {
      performance.mark(label);
    } catch {
      // performance API not available in all contexts
    }
  }

  /**
   * Measure elapsed time between two marks.
   * Returns duration in ms, or -1 if marks not found.
   */
  static measure(name: string, startMark: string, endMark?: string): number {
    try {
      const entry = performance.measure(name, startMark, endMark);
      const measure: PerformanceMeasure = {
        name,
        durationMs: Math.round(entry.duration * 100) / 100,
        startMs: Math.round(entry.startTime * 100) / 100,
        endMs: Math.round((entry.startTime + entry.duration) * 100) / 100,
        timestamp: new Date().toISOString(),
      };

      // Circular buffer — keep only last MAX_MEASURES
      if (PerformanceService.measures.length >= PerformanceService.MAX_MEASURES) {
        PerformanceService.measures.shift();
      }
      PerformanceService.measures.push(measure);

      return measure.durationMs;
    } catch {
      return -1;
    }
  }

  /**
   * Time an async operation with automatic start/end marks.
   * Usage: const result = await PerformanceService.time("analyze", async () => fn())
   */
  static async time<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const startMark = `${name}:start`;
    const endMark = `${name}:end`;
    PerformanceService.mark(startMark);
    try {
      const result = await fn();
      PerformanceService.mark(endMark);
      PerformanceService.measure(name, startMark, endMark);
      return result;
    } catch (err) {
      PerformanceService.mark(endMark);
      PerformanceService.measure(`${name}:error`, startMark, endMark);
      throw err;
    }
  }

  /**
   * Time a sync operation.
   */
  static timeSync<T>(name: string, fn: () => T): T {
    const startMark = `${name}:start`;
    const endMark = `${name}:end`;
    PerformanceService.mark(startMark);
    const result = fn();
    PerformanceService.mark(endMark);
    PerformanceService.measure(name, startMark, endMark);
    return result;
  }

  /**
   * Get all recorded performance measures.
   */
  static getMetrics(): PerformanceMeasure[] {
    return [...PerformanceService.measures];
  }

  /**
   * Get the latest measure for a given name.
   */
  static getLatest(name: string): PerformanceMeasure | undefined {
    return [...PerformanceService.measures]
      .reverse()
      .find((m) => m.name === name);
  }

  /**
   * Emit a summary report to console (stripped by Terser in production).
   */
  static logReport(): void {
    console.group("[CounterGuard] Performance Report");
    PerformanceService.measures.forEach((m) => {
      const bar = "█".repeat(Math.min(30, Math.ceil(m.durationMs / 10)));
      console.log(`  ${m.name.padEnd(32)} ${String(m.durationMs).padStart(7)}ms  ${bar}`);
    });
    console.groupEnd();
  }

  /**
   * Clear all recorded measures.
   */
  static clear(): void {
    PerformanceService.measures = [];
    try {
      performance.clearMarks();
      performance.clearMeasures();
    } catch {
      // noop
    }
  }

  /**
   * Get a summary object for display in popup debug panel.
   */
  static getSummary(): { totalMeasures: number; slowestMs: number; fastestMs: number; avgMs: number } {
    const all = PerformanceService.measures;
    if (all.length === 0) return { totalMeasures: 0, slowestMs: 0, fastestMs: 0, avgMs: 0 };

    const durations = all.map((m) => m.durationMs);
    return {
      totalMeasures: all.length,
      slowestMs: Math.max(...durations),
      fastestMs: Math.min(...durations),
      avgMs: Math.round(durations.reduce((a, b) => a + b, 0) / durations.length),
    };
  }
}
