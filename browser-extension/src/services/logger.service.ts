/**
 * logger.service.ts — Prefix-tagged structured console logging for Chrome extension
 */

export class ExtensionLogger {
  private static PREFIX = "[CounterGuard Extension]";

  static info(message: string, ...args: unknown[]): void {
    console.log(`${this.PREFIX} ℹ️ ${message}`, ...args);
  }

  static warn(message: string, ...args: unknown[]): void {
    console.warn(`${this.PREFIX} ⚠️ ${message}`, ...args);
  }

  static error(message: string, ...args: unknown[]): void {
    console.error(`${this.PREFIX} ❌ ${message}`, ...args);
  }

  static debug(message: string, ...args: unknown[]): void {
    console.debug(`${this.PREFIX} 🔍 ${message}`, ...args);
  }
}
