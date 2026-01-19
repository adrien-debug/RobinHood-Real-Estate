'use client'

import { FileDown } from 'lucide-react'

interface ExportPdfProps {
  targetId?: string
  filename?: string
  className?: string
}

export function ExportPdf({ targetId = 'export-content', filename = 'report', className }: ExportPdfProps) {
  const handleExport = () => {
    const content = targetId ? document.getElementById(targetId) : document.body
    if (!content) {
      console.error('Export target not found')
      return
    }

    // Create print-friendly version
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      alert('Please allow popups to export PDF')
      return
    }

    const styles = `
      <style>
        * { box-sizing: border-box; }
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding: 20px;
          background: #fff;
          color: #1a1a1a;
        }
        .card { 
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
          break-inside: avoid;
        }
        table { 
          width: 100%;
          border-collapse: collapse;
          margin: 16px 0;
        }
        th, td { 
          border: 1px solid #e5e5e5;
          padding: 8px;
          text-align: left;
          font-size: 12px;
        }
        th { background: #f5f5f5; font-weight: 600; }
        h1, h2, h3 { color: #1a1a1a; margin: 0 0 8px 0; }
        .text-muted { color: #666; font-size: 12px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        @media print {
          body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        }
        .header { 
          display: flex; 
          justify-content: space-between; 
          align-items: center;
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 2px solid #10B981;
        }
        .logo { font-size: 24px; font-weight: bold; color: #10B981; }
        .date { font-size: 12px; color: #666; }
      </style>
    `

    const date = new Date().toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>${filename}</title>
          ${styles}
        </head>
        <body>
          <div class="header">
            <div class="logo">Robin - Dubai Real Estate Intelligence</div>
            <div class="date">Généré le ${date}</div>
          </div>
          ${content.innerHTML}
        </body>
      </html>
    `)
    printWindow.document.close()

    setTimeout(() => {
      printWindow.print()
    }, 500)
  }

  return (
    <button
      onClick={handleExport}
      className={`btn-secondary flex items-center gap-2 ${className || ''}`}
      title="Exporter en PDF"
    >
      <FileDown className="w-4 h-4" />
      <span className="hidden sm:inline">PDF</span>
    </button>
  )
}
