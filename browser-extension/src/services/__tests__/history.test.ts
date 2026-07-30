import { describe, it, expect, beforeEach, vi } from "vitest";
import { HistoryService, InvestigationHistoryItem } from "../history.service";

describe("HistoryService Unit Test Suite", () => {
  beforeEach(async () => {
    await HistoryService.clearHistory();
  });

  it("adds investigation record to history and retrieves it", async () => {
    const item = await HistoryService.addRecord({
      investigationId: "inv-test-101",
      evidenceId: "ev-test-101",
      productTitle: "Test Wireless Earbuds Replica",
      sellerName: "Unverified Seller Co",
      marketplace: "Amazon",
      riskScore: 88.5,
      threatLevel: "HIGH",
      recommendation: "IMMEDIATE TAKEDOWN RECOMMENDED",
      url: "https://www.amazon.in/dp/B0TEST101",
    });

    expect(item.id).toBeDefined();
    expect(item.timestamp).toBeDefined();

    const history = await HistoryService.getHistory();
    expect(history.length).toBe(1);
    expect(history[0].investigationId).toBe("inv-test-101");
    expect(history[0].riskScore).toBe(88.5);
  });

  it("deletes individual history record by ID", async () => {
    const item1 = await HistoryService.addRecord({
      investigationId: "inv-test-201",
      evidenceId: "ev-201",
      productTitle: "Item 1",
      sellerName: "Seller A",
      marketplace: "Flipkart",
      riskScore: 40,
      threatLevel: "MEDIUM",
      recommendation: "INVESTIGATE",
      url: "https://flipkart.com/p1",
    });

    const item2 = await HistoryService.addRecord({
      investigationId: "inv-test-202",
      evidenceId: "ev-202",
      productTitle: "Item 2",
      sellerName: "Seller B",
      marketplace: "Myntra",
      riskScore: 10,
      threatLevel: "SAFE",
      recommendation: "CLEAN",
      url: "https://myntra.com/p2",
    });

    expect((await HistoryService.getHistory()).length).toBe(2);

    await HistoryService.deleteRecord(item1.id);
    const history = await HistoryService.getHistory();
    expect(history.length).toBe(1);
    expect(history[0].id).toBe(item2.id);
  });

  it("clears all stored investigation history", async () => {
    await HistoryService.addRecord({
      investigationId: "inv-301",
      evidenceId: "ev-301",
      productTitle: "Item 301",
      sellerName: "Seller C",
      marketplace: "AJIO",
      riskScore: 75,
      threatLevel: "HIGH",
      recommendation: "TAKDOWM",
      url: "https://ajio.com/p301",
    });

    expect((await HistoryService.getHistory()).length).toBe(1);

    await HistoryService.clearHistory();
    expect((await HistoryService.getHistory()).length).toBe(0);
  });

  it("formats valid JSON export payload", async () => {
    const sampleRecord: InvestigationHistoryItem = {
      id: "hist-1",
      investigationId: "inv-sample",
      evidenceId: "ev-sample",
      productTitle: "Sample Product",
      sellerName: "Sample Seller",
      marketplace: "Amazon",
      riskScore: 90,
      threatLevel: "CRITICAL",
      recommendation: "TAKDOWM",
      url: "https://amazon.in/sample",
      timestamp: new Date().toISOString(),
    };

    const exportedJson = HistoryService.exportHistoryJson([sampleRecord]);
    const parsed = JSON.parse(exportedJson);

    expect(parsed.total_records).toBe(1);
    expect(parsed.records[0].investigationId).toBe("inv-sample");
  });
});
