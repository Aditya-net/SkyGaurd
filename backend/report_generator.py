import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

def build_15day_pdf_report(summary: dict) -> bytes:
    """Generate a high-grade 15-Day PDF Analysis Report for SkyGuard SIH Demo."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#031018"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("SKYGUARD — NATIONAL WEATHER MONITORING NETWORK", title_style))
    story.append(Paragraph("Weather Station Anomaly Detection System • 15-Day Network Analysis Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # Meta Overview Box
    period_label = summary.get("period_label", "Days 1–15")
    start_time = summary.get("start_time", "N/A")
    end_time = summary.get("end_time", "N/A")
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    meta_data = [
        [
            Paragraph(f"<b>Report Period:</b> {period_label}", body_style),
            Paragraph(f"<b>Timeline Range:</b> {start_time} to {end_time}", body_style),
        ],
        [
            Paragraph(f"<b>Report Generated:</b> {gen_time}", body_style),
            Paragraph(f"<b>Detection Model:</b> SkyGuard V3 Random Forest (42 Features)", body_style),
        ]
    ]

    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Executive Summary Cards Table
    story.append(Paragraph("1. EXECUTIVE SUMMARY & NETWORK HEALTH", section_heading))

    total_st = summary.get("total_stations", 20)
    normal_st = summary.get("normal_stations_count", 20)
    anom_st = summary.get("anomalous_stations_count", 0)
    total_anom = summary.get("total_anomalies", 0)
    health_pct = summary.get("network_health_pct", 100.0)
    affected_sensor = summary.get("most_affected_sensor", "None")
    common_fault = summary.get("most_common_fault", "None")

    kpi_data = [
        [
            Paragraph("<b>Total Stations</b>", body_style),
            Paragraph("<b>Normal / Anomalous</b>", body_style),
            Paragraph("<b>Total Anomalies</b>", body_style),
            Paragraph("<b>Network Health</b>", body_style),
            Paragraph("<b>Primary Fault</b>", body_style),
        ],
        [
            Paragraph(f"<font size=12 color='#0f172a'><b>{total_st}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#16a34a'><b>{normal_st}</b></font> / <font size=12 color='#dc2626'><b>{anom_st}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#dc2626'><b>{total_anom}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#0284c7'><b>{health_pct}%</b></font>", body_style),
            Paragraph(f"<font size=10 color='#0f172a'><b>{affected_sensor} {common_fault}</b></font>", body_style),
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[108, 108, 108, 108, 108])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # Station Breakdown Table
    story.append(Paragraph("2. STATION-BY-STATION ANALYSIS", section_heading))

    headers = ["ID", "Station Name", "Location", "Readings", "Avg Temp", "Avg Rhum", "Avg Pres", "Anomalies", "Fault Sensors", "Max Prob"]
    st_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

    for st in summary.get("stations", []):
        st_rows.append([
            Paragraph(str(st["station_id"]), table_cell_style),
            Paragraph(st["name"], table_cell_style),
            Paragraph(st["location"], table_cell_style),
            Paragraph(str(st["readings_count"]), table_cell_style),
            Paragraph(f"{st['avg_temp']}°C", table_cell_style),
            Paragraph(f"{st['avg_rhum']}%", table_cell_style),
            Paragraph(f"{st['avg_pres']}", table_cell_style),
            Paragraph(f"<font color='{'#dc2626' if st['anomaly_count'] > 0 else '#16a34a'}'><b>{st['anomaly_count']}</b></font>", table_cell_style),
            Paragraph(st["fault_sensors"], table_cell_style),
            Paragraph(f"{st['max_prob']}%", table_cell_style),
        ])

    st_table = Table(st_rows, colWidths=[28, 95, 75, 45, 48, 48, 45, 52, 60, 44])
    st_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(st_table)
    story.append(Spacer(1, 10))

    # Anomaly Event Log Table
    anom_logs = summary.get("anomaly_logs", [])
    if anom_logs:
        story.append(Paragraph("3. DETECTED ANOMALY EVENT LOG SNAPSHOT", section_heading))
        log_headers = ["Timestamp", "Station ID", "Station Name", "Fault Sensor", "Fault Type", "Risk Prob", "Confidence"]
        log_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in log_headers]]

        for log in anom_logs[:12]: # first 12 logs for page fit
            log_rows.append([
                Paragraph(log["timestamp"], table_cell_style),
                Paragraph(str(log["station_id"]), table_cell_style),
                Paragraph(log["name"], table_cell_style),
                Paragraph(log["fault_sensor"], table_cell_style),
                Paragraph(log["fault_type"], table_cell_style),
                Paragraph(f"<font color='#dc2626'><b>{log['probability']}%</b></font>", table_cell_style),
                Paragraph(f"{log['confidence']}%", table_cell_style),
            ])

        log_table = Table(log_rows, colWidths=[90, 45, 115, 65, 65, 55, 55])
        log_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#dc2626")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#fecaca")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(log_table)
        story.append(Spacer(1, 10))

    # Conclusion & Operational Recommendations
    story.append(Paragraph("4. CONCLUSION & RECOMMENDED MAINTENANCE ACTION", section_heading))

    conclusion_text = (
        f"During the {period_label} monitoring timeline ({start_time} to {end_time}), the SkyGuard AI engine evaluated "
        f"a total of {summary.get('total_readings', 0)} hourly observations across all {total_st} weather stations in India. "
        f"The network maintained an overall operational health rating of <b>{health_pct}%</b>. "
    )

    if total_anom > 0:
        conclusion_text += (
            f"A total of <b>{total_anom} sensor anomaly events</b> were detected across {anom_st} station(s). "
            f"The primary affected parameter was <b>{affected_sensor}</b> with <b>{common_fault}</b> being the predominant fault characterization. "
            f"It is recommended to dispatch field maintenance technicians to inspect sensor wiring, transducer baselines, and ADC shielding at the flagged stations."
        )
    else:
        conclusion_text += (
            "Zero sensor anomalies were detected during this period. All weather station sensors operated cleanly within nominal tolerances."
        )

    story.append(Paragraph(conclusion_text, body_style))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6))
    story.append(Paragraph("<b>SkyGuard AI Weather Intelligence Platform</b> • Official Operational Analysis Report", ParagraphStyle("FooterNote", parent=body_style, fontSize=7, textColor=colors.HexColor("#64748b"), alignment=1)))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
