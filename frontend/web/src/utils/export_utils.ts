/**
 * export_utils.ts — Phase 9: Enterprise Export Center Utilities
 * Functions to export Discovery Results, Product Reports, and Listing Comparisons to CSV, JSON, and PDF.
 */
import type { ListingCandidate, ProductIntelligenceReport } from '../types/discovery';

/** Export candidate listings to CSV */
export function exportCandidatesToCSV(candidates: ListingCandidate[], filename = 'counterguard_discovery_results.csv'): void {
  if (!candidates || candidates.length === 0) return;

  const headers = ['Candidate ID', 'Marketplace', 'Product Title', 'Price (INR)', 'Seller', 'Availability', 'Confidence', 'URL'];
  const rows = candidates.map((c) => [
    c.id,
    `"${c.marketplace.replace(/"/g, '""')}"`,
    `"${c.title.replace(/"/g, '""')}"`,
    c.price,
    `"${c.seller.replace(/"/g, '""')}"`,
    `"${c.availability.replace(/"/g, '""')}"`,
    `${Math.round((c.confidence ?? 0.85) * 100)}%`,
    `"${c.url.replace(/"/g, '""')}"`,
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/** Export payload to formatted JSON */
export function exportToJSON(data: unknown, filename = 'counterguard_intelligence_export.json'): void {
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** Export Product Intelligence Report to printable PDF format */
export function exportReportToPDF(report: ProductIntelligenceReport): void {
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;

  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>CounterGuard Executive Report - ${report.product_name}</title>
        <style>
          body { font-family: system-ui, -apple-system, sans-serif; padding: 40px; color: #0f172a; line-height: 1.5; }
          h1 { font-size: 24px; color: #1e1b4b; border-bottom: 2px solid #6366f1; padding-bottom: 10px; }
          .badge { display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 12px; }
          .HIGH, .CRITICAL { background: #fee2e2; color: #991b1b; }
          .MEDIUM { background: #fef3c7; color: #92400e; }
          .LOW { background: #dcfce7; color: #166534; }
          .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
          .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; }
          .card-title { font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase; }
          .card-val { font-size: 20px; font-weight: bold; margin-top: 5px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-size: 12px; }
          th { background: #f1f5f9; font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>CounterGuard Enterprise Product Intelligence Report</h1>
        <div><strong>Product:</strong> ${report.product_name} | <strong>Generated:</strong> ${new Date(report.generated_at).toLocaleString()}</div>

        <div className="grid">
          <div className="card">
            <div className="card-title">Overall Risk Score</div>
            <div className="card-val">${report.overall_product_risk}/100 <span className="badge ${report.overall_risk_level}">${report.overall_risk_level}</span></div>
          </div>
          <div className="card">
            <div className="card-title">Total Audited</div>
            <div className="card-val">${report.total_listings}</div>
          </div>
          <div className="card">
            <div className="card-title">Highest Risk Platform</div>
            <div className="card-val" style="color: #dc2626;">${report.highest_risk_marketplace || 'N/A'}</div>
          </div>
          <div className="card">
            <div className="card-title">Recommended Partner</div>
            <div className="card-val" style="color: #16a34a; font-size: 14px;">${report.recommended_seller || 'Official Store'}</div>
          </div>
        </div>

        <h3>Coordinator Executive Summary</h3>
        <p style="background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px;">${report.coordinator_summary}</p>

        <h3>Investigated Listings Breakdown</h3>
        <table>
          <thead>
            <tr>
              <th>Platform</th>
              <th>Title</th>
              <th>Seller</th>
              <th>Price (INR)</th>
              <th>Risk Score</th>
              <th>Verdict</th>
            </tr>
          </thead>
          <tbody>
            ${report.investigations.map((inv) => `
              <tr>
                <td><strong>${inv.marketplace}</strong></td>
                <td>${inv.title}</td>
                <td>${inv.seller}</td>
                <td>₹${inv.price.toLocaleString()}</td>
                <td>${inv.risk_score}/100</td>
                <td><span className="badge ${inv.verdict}">${inv.verdict}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <script>window.print();</script>
      </body>
    </html>
  `;

  printWindow.document.write(html);
  printWindow.document.close();
}
