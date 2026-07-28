import type { InvestigationWorkspaceDetails } from '../types/investigations';

export const ReportExportService = {
  generatePrintableReport(details: InvestigationWorkspaceDetails) {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const createdDate = details.createdAt ? new Date(details.createdAt).toLocaleString() : 'N/A';
    const riskColor = details.riskScore > 50 ? '#dc2626' : '#059669';

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>CounterGuard Cyber Intelligence Investigation Report - ${details.id}</title>
          <style>
            body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; }
            .header { border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
            .logo { font-size: 24px; font-weight: 900; color: #0f172a; letter-spacing: -0.5px; }
            .logo span { color: #2563eb; }
            .badge { padding: 4px 12px; border-radius: 6px; font-weight: 800; font-size: 12px; text-transform: uppercase; }
            .verdict-box { background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 30px; }
            .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
            .metric-card { background: #f1f5f9; padding: 15px; border-radius: 8px; text-align: center; }
            .metric-value { font-size: 20px; font-weight: 800; font-family: monospace; }
            .section-title { font-size: 16px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin-top: 30px; margin-bottom: 15px; }
            .evidence-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .evidence-table th, .evidence-table td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 12px; }
            .evidence-table th { background: #f8fafc; }
            .footer { margin-top: 50px; border-top: 1px solid #cbd5e1; padding-top: 15px; font-size: 11px; color: #64748b; text-align: center; }
          </style>
        </head>
        <body>
          <div class="header">
            <div>
              <div class="logo">Counter<span>Guard</span></div>
              <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Automated Cyber Intelligence Platform</div>
            </div>
            <div style="text-align: right;">
              <div style="font-weight: bold; font-size: 14px;">CASE REPORT: INV-${details.id.substring(0, 8).toUpperCase()}</div>
              <div style="font-size: 11px; color: #64748b;">Generated: ${new Date().toLocaleString()}</div>
            </div>
          </div>

          <div class="verdict-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">Final Verdict Assessment</span>
              <span class="badge" style="background: ${riskColor}15; color: ${riskColor}; border: 1px solid ${riskColor}; font-size: 14px;">
                ${details.finalVerdict?.toUpperCase() || 'EVALUATED'} (${details.riskScore}/100)
              </span>
            </div>
            <p style="font-size: 14px; font-weight: 500; color: #334155; margin: 0;">${details.aiSummary}</p>
          </div>

          <div class="metric-grid">
            <div class="metric-card">
              <div style="font-size: 10px; font-weight: 700; color: #64748b;">RISK SCORE</div>
              <div class="metric-value" style="color: ${riskColor};">${details.riskScore}/100</div>
            </div>
            <div class="metric-card">
              <div style="font-size: 10px; font-weight: 700; color: #64748b;">VERDICT CONFIDENCE</div>
              <div class="metric-value" style="color: #2563eb;">${details.verdictConfidence}%</div>
            </div>
            <div class="metric-card">
              <div style="font-size: 10px; font-weight: 700; color: #64748b;">MARKETPLACE</div>
              <div class="metric-value" style="font-size: 14px; margin-top: 4px;">${details.marketplace}</div>
            </div>
            <div class="metric-card">
              <div style="font-size: 10px; font-weight: 700; color: #64748b;">CASE CREATED</div>
              <div class="metric-value" style="font-size: 11px; margin-top: 6px;">${createdDate}</div>
            </div>
          </div>

          <div class="section-title">Grounded AI Reasoning & Explainability</div>
          <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 13px;">
            ${details.explainability?.reasoning || details.aiSummary}
          </div>

          <div class="section-title">Specialist Swarm Evidence Timeline</div>
          <table class="evidence-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Title / Action</th>
                <th>Agent</th>
                <th>Severity</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${(details.timeline || []).map(ev => `
                <tr>
                  <td style="font-family: monospace;">${ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : 'Now'}</td>
                  <td><strong>${ev.title}</strong></td>
                  <td>${ev.agent || 'Specialist'}</td>
                  <td><span style="text-transform: uppercase; font-weight: bold; font-size: 10px;">${ev.severity || 'INFO'}</span></td>
                  <td>${ev.description}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div class="footer">
            CounterGuard AI Cyber Intelligence Platform — Confidential Brand Security Report
          </div>
        </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 400);
  }
};
