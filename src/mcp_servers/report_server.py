"""
Report Agent MCP Server - "Professional Reports at Your Service"

This server provides automated penetration testing report generation for the Kali Agents system.
It generates professional PDF and HTML reports with executive summaries, technical findings,
and remediation recommendations.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import tempfile

from fastmcp import FastMCP, Context
from src.config.settings import REPORT_CONFIG

# Import reporting libraries
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


# Create the MCP server instance
mcp = FastMCP("ReportAgent")


# In-memory report storage
REPORTS = {}


@mcp.tool
async def create_report(
    title: str,
    target: str,
    tester: Optional[str] = None,
    template: str = "default",
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Create a new penetration testing report.

    Args:
        title: Report title (e.g., "Security Assessment for ACME Corp")
        target: Target system/network being assessed
        tester: Name of penetration tester (default: from config)
        template: Report template to use (default, executive, technical, compliance)

    Returns:
        Dictionary containing report_id and initial metadata
    """
    if ctx:
        await ctx.info(f"📝 Creating new report: {title}")

    # Validate template
    allowed_templates = ["default", "executive", "technical", "compliance"]
    if template not in allowed_templates:
        return {
            "status": "failed",
            "error": f"Invalid template. Allowed: {allowed_templates}"
        }

    # Generate report ID
    report_id = str(uuid.uuid4())

    # Get tester name from config if not provided
    if tester is None:
        tester = REPORT_CONFIG.get("pentester_name", "Security Analyst")

    # Create report structure
    report = {
        "report_id": report_id,
        "title": title,
        "target": target,
        "tester": tester,
        "company": REPORT_CONFIG.get("company_name", "Security Firm"),
        "template": template,
        "created_at": datetime.now().isoformat(),
        "sections": {
            "executive_summary": {"content": "", "findings_count": 0},
            "scope": {"in_scope": [], "out_scope": []},
            "methodology": {"steps": []},
            "findings": [],
            "recommendations": [],
            "appendices": []
        },
        "metadata": {
            "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "total_findings": 0,
            "status": "draft"
        }
    }

    # Store report
    REPORTS[report_id] = report

    if ctx:
        await ctx.info(f"✅ Report created with ID: {report_id}")

    return {
        "status": "created",
        "report_id": report_id,
        "title": title,
        "template": template
    }


@mcp.tool
async def add_executive_summary(
    report_id: str,
    summary: Optional[str] = None,
    auto_generate: bool = False,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Add or generate executive summary for report.

    Args:
        report_id: Report identifier
        summary: Executive summary text (if not auto-generating)
        auto_generate: Use LLM to generate summary from findings

    Returns:
        Updated report section
    """
    if ctx:
        await ctx.info(f"📝 Adding executive summary to report {report_id}")

    # Validate report exists
    if report_id not in REPORTS:
        return {
            "status": "failed",
            "error": f"Report not found: {report_id}"
        }

    report = REPORTS[report_id]

    if auto_generate:
        # Auto-generate summary from findings
        summary = _generate_executive_summary(report)

    # Update report
    report["sections"]["executive_summary"]["content"] = summary
    report["sections"]["executive_summary"]["findings_count"] = len(report["sections"]["findings"])

    return {
        "status": "updated",
        "report_id": report_id,
        "executive_summary": summary[:200] + "..." if len(summary) > 200 else summary
    }


@mcp.tool
async def add_finding(
    report_id: str,
    title: str,
    severity: str,
    description: str,
    impact: str,
    remediation: str,
    cvss_score: Optional[float] = None,
    affected_assets: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Add a security finding to the report.

    Args:
        report_id: Report identifier
        title: Finding title (e.g., "SQL Injection in Login Form")
        severity: Severity level (critical, high, medium, low, info)
        description: Detailed description of the vulnerability
        impact: Business and technical impact
        remediation: Remediation steps
        cvss_score: CVSS v3.1 score (0.0-10.0)
        affected_assets: List of affected systems/URLs
        evidence: List of evidence (screenshots, logs, etc.)

    Returns:
        Updated finding count and metadata
    """
    if ctx:
        await ctx.info(f"📝 Adding finding to report {report_id}: {title}")

    # Validate report exists
    if report_id not in REPORTS:
        return {
            "status": "failed",
            "error": f"Report not found: {report_id}"
        }

    # Validate severity
    allowed_severities = ["critical", "high", "medium", "low", "info"]
    if severity.lower() not in allowed_severities:
        return {
            "status": "failed",
            "error": f"Invalid severity. Allowed: {allowed_severities}"
        }

    # Validate CVSS score if provided
    if cvss_score is not None and not (0.0 <= cvss_score <= 10.0):
        return {
            "status": "failed",
            "error": "CVSS score must be between 0.0 and 10.0"
        }

    report = REPORTS[report_id]

    # Create finding
    finding = {
        "finding_id": str(uuid.uuid4()),
        "title": title,
        "severity": severity.lower(),
        "description": description,
        "impact": impact,
        "remediation": remediation,
        "cvss_score": cvss_score,
        "affected_assets": affected_assets or [],
        "evidence": evidence or [],
        "added_at": datetime.now().isoformat()
    }

    # Add to report
    report["sections"]["findings"].append(finding)

    # Update metadata
    report["metadata"]["severity_counts"][severity.lower()] += 1
    report["metadata"]["total_findings"] = len(report["sections"]["findings"])

    if ctx:
        total = report["metadata"]["total_findings"]
        await ctx.info(f"✅ Finding added! Total findings: {total}")

    return {
        "status": "added",
        "report_id": report_id,
        "finding_id": finding["finding_id"],
        "total_findings": report["metadata"]["total_findings"],
        "severity_counts": report["metadata"]["severity_counts"]
    }


@mcp.tool
async def generate_pdf(
    report_id: str,
    output_path: Optional[str] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Generate PDF report.

    Args:
        report_id: Report identifier
        output_path: Output file path (default: auto-generated in output_dir)

    Returns:
        Path to generated PDF file
    """
    if ctx:
        await ctx.info(f"📄 Generating PDF for report {report_id}")

    # Check if reportlab is available
    if not REPORTLAB_AVAILABLE:
        return {
            "status": "failed",
            "error": "ReportLab not installed. Install with: pip install reportlab"
        }

    # Validate report exists
    if report_id not in REPORTS:
        return {
            "status": "failed",
            "error": f"Report not found: {report_id}"
        }

    report = REPORTS[report_id]

    # Generate output path if not provided
    if output_path is None:
        output_dir = REPORT_CONFIG.get("output_dir", Path("./reports"))
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"report_{report_id[:8]}_{timestamp}.pdf"
    else:
        output_path = Path(output_path)

    try:
        # Generate PDF
        _generate_pdf_report(report, str(output_path))

        if ctx:
            await ctx.info(f"✅ PDF generated: {output_path}")

        return {
            "status": "generated",
            "report_id": report_id,
            "output_path": str(output_path),
            "format": "pdf"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "report_id": report_id
        }


@mcp.tool
async def generate_html(
    report_id: str,
    output_path: Optional[str] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Generate HTML report.

    Args:
        report_id: Report identifier
        output_path: Output file path (default: auto-generated in output_dir)

    Returns:
        Path to generated HTML file
    """
    if ctx:
        await ctx.info(f"🌐 Generating HTML for report {report_id}")

    # Validate report exists
    if report_id not in REPORTS:
        return {
            "status": "failed",
            "error": f"Report not found: {report_id}"
        }

    report = REPORTS[report_id]

    # Generate output path if not provided
    if output_path is None:
        output_dir = REPORT_CONFIG.get("output_dir", Path("./reports"))
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"report_{report_id[:8]}_{timestamp}.html"
    else:
        output_path = Path(output_path)

    try:
        # Generate HTML
        html_content = _generate_html_report(report)

        # Write to file
        with open(output_path, 'w') as f:
            f.write(html_content)

        if ctx:
            await ctx.info(f"✅ HTML generated: {output_path}")

        return {
            "status": "generated",
            "report_id": report_id,
            "output_path": str(output_path),
            "format": "html"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "report_id": report_id
        }


@mcp.tool
async def list_reports(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    List all reports in the system.

    Returns:
        List of reports with metadata
    """
    reports_list = [
        {
            "report_id": report_id,
            "title": report["title"],
            "target": report["target"],
            "created_at": report["created_at"],
            "total_findings": report["metadata"]["total_findings"],
            "severity_counts": report["metadata"]["severity_counts"],
            "status": report["metadata"]["status"]
        }
        for report_id, report in REPORTS.items()
    ]

    return {
        "status": "success",
        "total_reports": len(reports_list),
        "reports": reports_list
    }


# Helper Functions

def _generate_executive_summary(report: Dict[str, Any]) -> str:
    """Generate executive summary from findings."""
    findings = report["sections"]["findings"]
    severity_counts = report["metadata"]["severity_counts"]

    # Build summary
    summary_parts = []

    # Introduction
    summary_parts.append(
        f"This report presents the findings from a security assessment of {report['target']} "
        f"conducted by {report['company']} on {datetime.now().strftime('%B %d, %Y')}."
    )

    # Risk overview
    total_findings = len(findings)
    critical_count = severity_counts.get("critical", 0)
    high_count = severity_counts.get("high", 0)

    if critical_count > 0 or high_count > 0:
        risk_level = "HIGH"
        risk_desc = (
            f"The assessment identified {total_findings} security findings, including "
            f"{critical_count} critical and {high_count} high-severity vulnerabilities. "
            f"Immediate remediation is strongly recommended."
        )
    elif severity_counts.get("medium", 0) > 0:
        risk_level = "MEDIUM"
        risk_desc = (
            f"The assessment identified {total_findings} security findings. "
            f"While no critical vulnerabilities were found, remediation of medium-severity "
            f"issues is recommended to improve security posture."
        )
    else:
        risk_level = "LOW"
        risk_desc = (
            f"The assessment identified {total_findings} minor security findings. "
            f"The overall security posture is satisfactory."
        )

    summary_parts.append(f"\n**Overall Risk Assessment: {risk_level}**\n")
    summary_parts.append(risk_desc)

    # Top findings
    if findings:
        summary_parts.append("\n**Key Findings:**\n")

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(findings, key=lambda x: severity_order.get(x["severity"], 4))

        for i, finding in enumerate(sorted_findings[:5], 1):
            summary_parts.append(
                f"{i}. **{finding['title']}** (Severity: {finding['severity'].upper()})"
            )

    return "\n".join(summary_parts)


def _generate_pdf_report(report: Dict[str, Any], output_path: str) -> None:
    """Generate PDF report using ReportLab."""
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(report["title"], title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Target: {report['target']}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph(f"Prepared by: {report['tester']}", styles['Normal']))
    story.append(PageBreak())

    # Executive Summary
    if report["sections"]["executive_summary"]["content"]:
        story.append(Paragraph("Executive Summary", styles['Heading1']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(report["sections"]["executive_summary"]["content"], styles['Normal']))
        story.append(Spacer(1, 12))

    # Findings Summary
    story.append(Paragraph("Findings Summary", styles['Heading1']))
    story.append(Spacer(1, 12))

    # Severity table
    severity_data = [
        ['Severity', 'Count'],
        ['Critical', str(report["metadata"]["severity_counts"]["critical"])],
        ['High', str(report["metadata"]["severity_counts"]["high"])],
        ['Medium', str(report["metadata"]["severity_counts"]["medium"])],
        ['Low', str(report["metadata"]["severity_counts"]["low"])],
        ['Info', str(report["metadata"]["severity_counts"]["info"])],
    ]

    severity_table = Table(severity_data, colWidths=[2*inch, 1*inch])
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(severity_table)
    story.append(PageBreak())

    # Detailed Findings
    story.append(Paragraph("Detailed Findings", styles['Heading1']))
    story.append(Spacer(1, 12))

    for i, finding in enumerate(report["sections"]["findings"], 1):
        story.append(Paragraph(f"Finding #{i}: {finding['title']}", styles['Heading2']))
        story.append(Paragraph(f"<b>Severity:</b> {finding['severity'].upper()}", styles['Normal']))

        if finding.get("cvss_score"):
            story.append(Paragraph(f"<b>CVSS Score:</b> {finding['cvss_score']}", styles['Normal']))

        story.append(Paragraph(f"<b>Description:</b> {finding['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Impact:</b> {finding['impact']}", styles['Normal']))
        story.append(Paragraph(f"<b>Remediation:</b> {finding['remediation']}", styles['Normal']))
        story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)


def _generate_html_report(report: Dict[str, Any]) -> str:
    """Generate HTML report using Jinja2."""
    # HTML template
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ report.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
        .severity-critical { color: #d32f2f; font-weight: bold; }
        .severity-high { color: #f57c00; font-weight: bold; }
        .severity-medium { color: #fbc02d; font-weight: bold; }
        .severity-low { color: #388e3c; }
        .severity-info { color: #1976d2; }
        table { border-collapse: collapse; width: 50%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .finding { margin: 30px 0; padding: 20px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
    </style>
</head>
<body>
    <h1>{{ report.title }}</h1>
    <p><strong>Target:</strong> {{ report.target }}</p>
    <p><strong>Date:</strong> {{ date }}</p>
    <p><strong>Prepared by:</strong> {{ report.tester }}</p>

    <h2>Executive Summary</h2>
    <p>{{ report.sections.executive_summary.content }}</p>

    <h2>Findings Summary</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Count</th>
        </tr>
        {% for severity, count in report.metadata.severity_counts.items() %}
        <tr>
            <td class="severity-{{ severity }}">{{ severity|upper }}</td>
            <td>{{ count }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Detailed Findings</h2>
    {% for finding in report.sections.findings %}
    <div class="finding">
        <h3>{{ loop.index }}. {{ finding.title }}</h3>
        <p><strong class="severity-{{ finding.severity }}">Severity: {{ finding.severity|upper }}</strong></p>
        {% if finding.cvss_score %}
        <p><strong>CVSS Score:</strong> {{ finding.cvss_score }}</p>
        {% endif %}
        <p><strong>Description:</strong> {{ finding.description }}</p>
        <p><strong>Impact:</strong> {{ finding.impact }}</p>
        <p><strong>Remediation:</strong> {{ finding.remediation }}</p>
    </div>
    {% endfor %}
</body>
</html>
    """

    # Render template
    if JINJA2_AVAILABLE:
        template = Template(html_template)
        return template.render(
            report=report,
            date=datetime.now().strftime('%B %d, %Y')
        )
    else:
        # Fallback if Jinja2 not available
        return f"<html><body><h1>{report['title']}</h1><p>Jinja2 not installed</p></body></html>"


# Health check endpoint
@mcp.tool
async def health_check(ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Check report server health and library availability."""
    libraries_status = {
        "reportlab": REPORTLAB_AVAILABLE,
        "jinja2": JINJA2_AVAILABLE
    }

    all_available = all(libraries_status.values())

    return {
        "status": "healthy" if all_available else "degraded",
        "libraries": libraries_status,
        "total_reports": len(REPORTS),
        "server": "ReportAgent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
