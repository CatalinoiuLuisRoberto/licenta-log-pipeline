import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Directories
OUT_DIR = r"E:\Licenta-Log-Pipeline\SPM_Assignment"
os.makedirs(OUT_DIR, exist_ok=True)

NAVY = RGBColor(24, 60, 100)
STEEL = RGBColor(70, 95, 125)
TEXT_COLOR = RGBColor(40, 40, 40)
MUTED = RGBColor(100, 100, 100)

def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def base_doc():
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
    norm = doc.styles['Normal']
    norm.font.name = 'Calibri'
    norm.font.size = Pt(10.5)
    norm.font.color.rgb = TEXT_COLOR
    norm.paragraph_format.line_spacing = 1.15
    norm.paragraph_format.space_after = Pt(3)
    return doc

# ==========================================
# 1. GENERATE WBS DIAGRAM IMAGE (MATCHING UPLOADED STYLE)
# ==========================================
def generate_wbs_image():
    img_path = os.path.join(OUT_DIR, "WBS_Diagram.png")
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Styles
    box_props_root = dict(boxstyle='square,pad=0.6', facecolor='#F2F4F7', edgecolor='#1F4E79', linewidth=2.0)
    box_props_l1 = dict(boxstyle='square,pad=0.5', facecolor='#FFFFFF', edgecolor='#1F4E79', linewidth=1.5)
    box_props_l2 = dict(boxstyle='square,pad=0.4', facecolor='#FFFFFF', edgecolor='#595959', linewidth=1.0)

    # 1. ROOT
    rx, ry = 50, 93
    ax.text(rx, ry, "A Hybrid ML and LLM Pipeline for Log-Based\nIncident Detection and Remediation\n(LogAutoRemediate Platform)", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#1F4E79', bbox=box_props_root)

    # Level 1 Columns X positions
    col_x = [15, 38, 62, 85]
    l1_y = 78

    col_titles = [
        ("1. Managementul\nProiectului", [
            "1.1. Carta Proiectului (Project Charter)",
            "1.2. Scope Statement",
            "1.3. WBS & Structura de Lucru",
            "1.4. Planificarea Resurselor & Echipei",
            "1.5. Lista de Activitati (Activity List)",
            "1.6. Planificare Buget & Costuri",
            "1.7. Rapoarte de Progres & Riscuri",
            "1.8. Planificare Sprint-uri (SCRUM)"
        ]),
        ("2. Arhitectura SW", [
            "2.1. Specificarea Cerintelor (FR & NFR)",
            "2.2. Diagrama Use-Case & Actori",
            "2.3. Diagrama de Activitati (Pipeline Dataflow)",
            "2.4. Diagrama de Componente & Clase",
            "2.5. Modelul de Date (Template-uri & Metrici)"
        ]),
        ("3. Implementare SW", [
            "3.1. Modul Ingestie & Drain3 Template Miner",
            "3.2. Modul ML Anomaly Detection (Isolation Forest)",
            "3.3. Modul LLM Root-Cause & Patch Synthesis",
            "3.4. Modul Git Automation & SRE Sandbox",
            "3.5. Interfata Grafana Dashboard & Metrics"
        ]),
        ("4. Testare SW & QA", [
            "4.1. Testare de Performanta (Throughput Loguri)",
            "4.2. Testare de Securitate & Sandbox Containere",
            "4.3. Testare Acuratete ML & Validare Patch-uri"
        ])
    ]

    # Draw line from root down to horizontal spine
    ax.plot([rx, rx], [ry - 4.5, 84], color='#1F4E79', lw=1.5)
    ax.plot([col_x[0], col_x[-1]], [84, 84], color='#1F4E79', lw=1.5)

    for i, (l1_title, l2_items) in enumerate(col_titles):
        cx = col_x[i]
        # Drop down line to L1 box
        ax.plot([cx, cx], [84, l1_y + 3.2], color='#1F4E79', lw=1.5)
        # L1 Box
        ax.text(cx, l1_y, l1_title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1F4E79', bbox=box_props_l1)

        # Vertical spine for children
        spine_start_y = l1_y - 3.2
        spine_end_y = spine_start_y - (len(l2_items) * 6.5) + 3.0
        ax.plot([cx - 9, cx - 9], [spine_start_y, spine_end_y], color='#595959', lw=1.2)
        ax.plot([cx, cx - 9], [spine_start_y + 1.0, spine_start_y], color='#595959', lw=1.2)

        # Children boxes
        for j, item in enumerate(l2_items):
            iy = spine_start_y - (j * 6.5) - 1.5
            # Horizontal connector branch
            ax.plot([cx - 9, cx - 7], [iy, iy], color='#595959', lw=1.2)
            # Child Box
            ax.text(cx + 1, iy, item, ha='center', va='center', fontsize=8.0, color='#262626', bbox=box_props_l2, wrap=True)

    plt.tight_layout()
    plt.savefig(img_path, bbox_inches='tight', dpi=300)
    plt.close()
    print("WBS image generated successfully!")

# ==========================================
# 2. GENERATE PROJECT CHARTER (.DOCX)
# ==========================================
def generate_project_charter():
    doc = base_doc()

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_t.add_run("PROJECT CHARTER")
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Course: Software Project Management • Academic Year 2026–2027\nStandard PMBOK / PMI Aligned Template")
    r_sub.font.size = Pt(9.5)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED

    table = doc.add_table(rows=0, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    def add_section_header(title):
        row = table.add_row()
        c = row.cells[0]
        c.merge(row.cells[3])
        p = c.paragraphs[0]
        p.text = title
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.color.rgb = NAVY
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 80, 80, 120, 120)

    def add_row_2col(label1, val1, label2="", val2=""):
        row = table.add_row()
        c0, c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2], row.cells[3]
        if not label2 and not val2:
            c1.merge(c3)
            c0.paragraphs[0].text = label1
            c0.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].text = val1
            set_cell_background(c0, "F8F9F9")
            set_cell_margins(c0)
            set_cell_margins(c1)
        else:
            c0.paragraphs[0].text = label1
            c0.paragraphs[0].runs[0].font.bold = True
            c1.paragraphs[0].text = val1
            c2.paragraphs[0].text = label2
            c2.paragraphs[0].runs[0].font.bold = True
            c3.paragraphs[0].text = val2
            set_cell_background(c0, "F8F9F9")
            set_cell_background(c2, "F8F9F9")
            set_cell_margins(c0)
            set_cell_margins(c1)
            set_cell_margins(c2)
            set_cell_margins(c3)

    # 1. Project Information
    add_section_header("1. Project Information")
    add_row_2col("Project Name:", "A Hybrid ML and LLM Pipeline for Log-Based Incident Detection and Remediation (LogAutoRemediate)", "ID Number:", "PRJ-SPM-2026-01")
    add_row_2col("Project Description:", "An end-to-end cloud-native SRE platform that ingests unstructured server logs, mines semantic templates using Drain3, detects anomalies via Isolation Forest ML, and synthesizes validated bug-fix Pull Requests on Git via LLMs.", "", "")
    add_row_2col("Project Sponsor:", "Ș.l. dr. ing. Ionuț Murarețu (Computer Science & SRE Dept.)", "Program Manager:", "Head of CTI Department")
    add_row_2col("Project Manager:", "Cătălinoiu Luis-Roberto (CTI English)", "Organization(s):", "UNSTPB - Faculty of Automatic Control and Computers")
    add_row_2col("Target Start Date:", "15 October 2026", "Target End Date:", "15 June 2027")

    # 2. Business Need / Project Goal
    add_section_header("2. Business Need / Project Goal")
    goal_text = (
        "Modern cloud-native and server-side production applications generate massive, expensive log volumes. "
        "Diagnosing system outages manually takes hours of senior SRE time, driving up Mean Time to Resolution (MTTR). "
        "The goal of this project is to develop an automated 'closed-loop self-healing' platform that: "
        "(1) compresses logs by 90% via online template mining (Drain3); (2) flags abnormal event surges using lightweight ML; "
        "and (3) automatically analyzes code context, generates bug-fixing patches via LLM, and submits verified GitHub Pull Requests."
    )
    add_row_2col("Business Need & Goal:", goal_text, "", "")

    # 3. Project Scope
    add_section_header("3. Project Scope")
    in_scope = (
        "• Real-time log ingestion (FastAPI, Promtail, Syslog, JSON).\n"
        "• Online log template mining & clustering using Drain3.\n"
        "• Prometheus metrics export (/metrics) and Loki log storage.\n"
        "• Unsupervised anomaly detection model (Isolation Forest).\n"
        "• LLM diagnostic engine integrating Git source code context.\n"
        "• Automated Docker sandbox testing and GitHub Pull Request generation."
    )
    out_scope = (
        "• Blind/unreviewed automatic deployments directly to live production servers (requires human PR merge).\n"
        "• Hardware-level or network firmware log diagnostics.\n"
        "• Commercial billing or proprietary cloud marketplace monetization modules."
    )
    add_row_2col("In Scope:", in_scope, "Out of Scope:", out_scope)

    # 4. Constraints, Risks, Assumptions & Budget
    add_section_header("4. Constraints, Risks, Assumptions & Budget")
    add_row_2col("Constraints:", "• Strict academic delivery timeline (Milestones in Nov 2026, Jan 2027, May 2027).\n• Must run on Docker containerized infrastructure with under 2GB RAM baseline.\n• Code fixes must be verified via automated regression tests before PR submission.", "", "")
    add_row_2col("Key Risks & Mitigation:", "• Risk 1: LLM hallucination in patch synthesis. -> Mitigation: Docker sandbox regression testing.\n• Risk 2: High API cost for LLM tokens. -> Mitigation: Preliminary filtering via Drain3 & ML.\n• Risk 3: Concept drift in log templates. -> Mitigation: Periodic Drain3 tree snapshot persistence.", "", "")
    add_row_2col("Assumptions:", "• Target applications follow standard logging practices (logging levels, stack traces).\n• Target repositories have existing unit/integration test suites.\n• Docker and GitHub REST API access are available.", "", "")
    add_row_2col("Project Budget:", "Total Estimated Budget: €85,000 (Simulated for 5-member team over 6 months):\n• Personnel Salaries: €74,400  • Cloud Infrastructure (AWS/GCP): €3,600\n• LLM API & Development Tooling (Jira, GitHub Enterprise): €7,000", "", "")

    # 5. Project Team & Key Milestones
    add_section_header("5. Project Team & Key Milestones")
    team_text = (
        "1. Cătălinoiu Luis-Roberto — Project Manager & Lead Architect (€2,500/mo)\n"
        "2. Alex Radu — Senior DevOps & SRE Engineer (€3,200/mo)\n"
        "3. Elena Popa — Machine Learning Specialist (€3,000/mo)\n"
        "4. Mihai Ionescu — Senior Backend Python Developer (€2,400/mo)\n"
        "5. Diana Dobre — QA & Test Automation Engineer (€1,800/mo)"
    )
    milestones_text = (
        "M1 (Nov 18, 2026): Core Ingestion & Drain3 Template Miner Prototype (Achieved)\n"
        "M2 (Dec 05, 2026): Prometheus & Grafana Monitoring Dashboard Operational\n"
        "M3 (Jan 15, 2027): Machine Learning Anomaly Detector (Isolation Forest) Trained\n"
        "M4 (Feb 20, 2027): LLM Contextual Root-Cause Engine & Git API Connector\n"
        "M5 (Mar 25, 2027): Sandboxed Docker Test Execution & Auto-PR Automation\n"
        "M6 (Apr 20, 2027): End-to-End System Integration Testing & Security Audit\n"
        "M7 (May 15, 2027): Performance Benchmarking & SRE Evaluation Report\n"
        "M8 (Jun 10, 2027): Final Thesis Defense & Project Sign-Off"
    )
    add_row_2col("Project Team (Name & Role):", team_text, "Key Project Milestones:", milestones_text)

    # Format table borders
    for row in table.rows:
        for cell in row.cells:
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)
            cell.paragraphs[0].paragraph_format.space_before = Pt(2)

    doc_path = os.path.join(OUT_DIR, "Project_Charter_SPM.docx")
    doc.save(doc_path)
    print("Project Charter docx generated!")

# ==========================================
# 3. GENERATE SCOPE STATEMENT (.DOCX)
# ==========================================
def generate_scope_statement():
    doc = base_doc()

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_t.add_run("PROJECT SCOPE STATEMENT")
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Course: Software Project Management • Deliverable 1.2\nProject: A Hybrid ML and LLM Pipeline for Log-Based Incident Detection and Remediation")
    r_sub.font.size = Pt(9.5)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED

    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    def add_scope_row(section_title, content):
        row = table.add_row()
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(5.0)
        c0.paragraphs[0].text = section_title
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(10)
        c0.paragraphs[0].runs[0].font.color.rgb = NAVY
        set_cell_background(c0, "F2F4F7")
        set_cell_margins(c0, 100, 100, 140, 140)

        c1.paragraphs[0].text = content
        c1.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_margins(c1, 100, 100, 140, 140)

    add_scope_row("Project Name & Header", 
                  "Project: LogAutoRemediate Pipeline\n"
                  "Project Sponsor: Ș.l. dr. ing. Ionuț Murarețu\n"
                  "Project Manager: Cătălinoiu Luis-Roberto\n"
                  "Target Kick-Off Date: 15 October 2026\n"
                  "Target Completion Date: 15 June 2027")

    add_scope_row("Project Goal", 
                  "Provide an enterprise-grade automated Site Reliability Engineering (SRE) tool that detects "
                  "server-side runtime anomalies from unstructured application log streams, performs semantic root-cause "
                  "diagnosis by correlating stack traces with Git source code, and submits verified code patches via automated "
                  "GitHub Pull Requests, drastically lowering MTTR (Mean Time to Resolution).")

    add_scope_row("Scope Description\n(Desired Final Product)", 
                  "The final product is a modular, containerized multi-service platform comprising:\n"
                  "1. Ingestion Engine: High-throughput HTTP/Syslog receiver connected to a Drain3 log parser.\n"
                  "2. Observability Core: Prometheus metrics exporter paired with Grafana Loki and pre-built Grafana dashboards.\n"
                  "3. Machine Learning Anomaly Detector: Isolation Forest algorithm trained on log template frequencies.\n"
                  "4. LLM Remediation Worker: LangChain/API worker that extracts relevant source code files from GitHub, "
                  "synthesizes a diff patch, validates it in an ephemeral Docker container with automated regression tests, "
                  "and publishes a fully documented Pull Request.")

    add_scope_row("Project Deliverables\n(In Scope vs. Out of Scope)", 
                  "IN-SCOPE DELIVERABLES:\n"
                  "• D1: Drain3 online log template mining microservice (FastAPI).\n"
                  "• D2: Multi-container orchestration stack (docker-compose.yml, Prometheus, Loki, Promtail, Grafana).\n"
                  "• D3: ML Anomaly Detection Engine with sliding frequency window evaluation.\n"
                  "• D4: GitHub API integration module for automated branch creation, commit, and Pull Request publishing.\n"
                  "• D5: Sandboxed test-runner executing test suites in isolated Docker environments.\n"
                  "• D6: Comprehensive test suite, documentation, and live demonstration benchmark.\n\n"
                  "OUT-OF-SCOPE (EXCLUSIONS):\n"
                  "• Direct unreviewed automated deployments into production branches (human review required on PR).\n"
                  "• Proprietary closed-source cloud APM vendor connectors.\n"
                  "• Mobile client application development.")

    add_scope_row("Challenges / Constraints", 
                  "• Latency Constraint: Anomaly detection inference must complete within 2 seconds of log burst arrival.\n"
                  "• Resource Constraint: Total base system footprint must not exceed 2 GB RAM when running idle.\n"
                  "• Safety Constraint: Synthetic patches must NEVER be merged without 100% pass rate in containerized test suites.\n"
                  "• API Rate Limits: GitHub API and LLM API quotas must be managed with backoff and caching mechanisms.")

    add_scope_row("Acceptance Criteria\n& Approvers", 
                  "SUCCESS FACTORS REQUIRED FOR FORMAL APPROVAL:\n"
                  "1. Log Compression: Drain3 must accurately reduce unstructured logs by >= 85% into deterministic templates.\n"
                  "2. Anomaly Detection: Isolation Forest must achieve >= 90% Recall on injected synthetic fault benchmarks.\n"
                  "3. Code Patch Validity: >= 80% of generated patches for common exception classes (NullPointer, Timeout, TypeMismatch) "
                  "must compile and pass existing test suites in the sandbox.\n"
                  "4. Traceability: 100% of Pull Requests must link the originating log session ID and stack trace.\n\n"
                  "FORMAL APPROVER: Ș.l. dr. ing. Ionuț Murarețu (Project Sponsor & Thesis Coordinator).")

    add_scope_row("Assumptions", 
                  "• Monitored microservices adhere to standard logging conventions (timestamps, severity levels, stack traces).\n"
                  "• Target software repositories possess automated unit/integration test suites that can be executed via CLI.\n"
                  "• Docker Desktop and stable internet connectivity for LLM APIs are available during runtime execution.")

    doc_path = os.path.join(OUT_DIR, "Scope_Statement_SPM.docx")
    doc.save(doc_path)
    print("Scope Statement docx generated!")

# ==========================================
# 4. GENERATE ACTIVITY LIST (.DOCX)
# ==========================================
def generate_activity_list():
    doc = base_doc()

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_t.add_run("ACTIVITY LIST")
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Course: Software Project Management • Project Scope Deliverable 1.5\nDetailed Work Activities, Predecessors, Durations, and Assigned Resources")
    r_sub.font.size = Pt(9.5)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED

    table = doc.add_table(rows=1, cols=7)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Act ID", "WBS Code", "Activity Name", "Detailed Description", "Pred.", "Dur (d)", "Assigned Resource"]
    col_widths = [Inches(0.6), Inches(0.7), Inches(1.5), Inches(2.2), Inches(0.6), Inches(0.5), Inches(1.3)]

    hdr_row = table.rows[0]
    for idx, text in enumerate(headers):
        c = hdr_row.cells[idx]
        c.width = col_widths[idx]
        p = c.paragraphs[0]
        p.text = text
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.color.rgb = NAVY
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 80, 80, 80, 80)

    activities = [
        # 1. Project Management
        ("ACT-01", "1.1", "Project Charter Drafting", "Define business goals, scope baseline, budget, team, and risks in formal charter.", "None", "5", "Project Manager"),
        ("ACT-02", "1.2", "Scope Statement Formulation", "Document in-scope deliverables, out-of-scope boundaries, acceptance criteria.", "ACT-01", "4", "Project Manager"),
        ("ACT-03", "1.3", "WBS Decomposition", "Decompose project work into 4 major packages and 21 detailed work elements.", "ACT-02", "3", "Project Manager"),
        ("ACT-04", "1.4", "Resource & Budget Planning", "Estimate team salaries, cloud infrastructure costs, and LLM API expenditures.", "ACT-03", "3", "Project Manager"),
        ("ACT-05", "1.5", "Activity List Definition", "Establish activity sequence, dependencies, durations, and resource assignments.", "ACT-04", "3", "Project Manager"),
        ("ACT-06", "1.8", "Sprint Setup & Jira Backlog", "Configure Atlassian Jira Scrum board, Epics, User Stories, and Sprint cycles.", "ACT-05", "2", "PM & Tech Team"),

        # 2. Software Architecture
        ("ACT-07", "2.1", "Functional & NFR Specs", "Author detailed specification for Drain3 mining, ML inference, and Git PR flow.", "ACT-02", "6", "Lead Architect"),
        ("ACT-08", "2.2", "Use-Case & Actor Modeling", "Draft UML use case diagrams covering SRE Operator, Git Server, and AI Agent.", "ACT-07", "4", "Backend Developer"),
        ("ACT-09", "2.3", "Pipeline Activity Diagram", "Document dataflow from raw log ingestion to Docker sandbox and Pull Request.", "ACT-07", "4", "Lead Architect"),
        ("ACT-10", "2.4", "Component & Class Design", "Design FastAPI routers, TemplateMiner wrapper, and GitHub API service classes.", "ACT-08", "5", "Backend Developer"),
        ("ACT-11", "2.5", "Data Schema Definition", "Define JSON template structures, Prometheus counter metrics, and Loki labels.", "ACT-10", "3", "DevOps & Backend"),

        # 3. Implementation
        ("ACT-12", "3.1.1", "Drain3 Parser Service", "Implement FastAPI template miner wrapping Drain3 with dynamic depth & sim_th.", "ACT-11", "8", "Backend Developer"),
        ("ACT-13", "3.1.2", "Mock Server Log Generator", "Build high-throughput synthetic log emitter with injected faults and bursts.", "ACT-12", "5", "QA Engineer"),
        ("ACT-14", "3.2.1", "ML Feature Extraction", "Build sliding-window frequency vectorizer aggregating template counts.", "ACT-12", "7", "ML Specialist"),
        ("ACT-15", "3.2.2", "Isolation Forest Training", "Train unsupervised anomaly detector on baseline log frequencies; tune threshold.", "ACT-14", "8", "ML Specialist"),
        ("ACT-16", "3.3.1", "LLM Context Builder", "Implement stack trace parser and GitHub source code fetcher for prompt injection.", "ACT-15", "9", "Lead Architect"),
        ("ACT-17", "3.3.2", "LLM Patch Generator", "Engineer prompt templates for unified git diff generation using Gemini/OpenAI.", "ACT-16", "8", "Lead Architect"),
        ("ACT-18", "3.4.1", "Docker Test Sandbox", "Build ephemeral container runner to apply diff patches and execute pytest suites.", "ACT-17", "7", "DevOps Engineer"),
        ("ACT-19", "3.4.2", "Git Automation & PR Creator", "Implement PyGithub client to create feature branches, commit fixes, and open PRs.", "ACT-18", "6", "Backend Developer"),
        ("ACT-20", "3.5.1", "Prometheus & Loki Stack", "Configure docker-compose.yml for Prometheus, Loki, Promtail log aggregator.", "ACT-11", "6", "DevOps Engineer"),
        ("ACT-21", "3.5.2", "Grafana Unified Dashboard", "Create Grafana dashboard correlating error count spikes with Loki log lines.", "ACT-20", "5", "DevOps Engineer"),

        # 4. Testing & QA
        ("ACT-22", "4.1", "Performance & Load Testing", "Benchmark system under 10,000 logs/sec; measure inference latency (<2s).", "ACT-21", "6", "QA Engineer"),
        ("ACT-23", "4.2", "Security & Sandbox Audit", "Verify Docker sandbox isolation; test containment of malicious or broken patches.", "ACT-18", "5", "DevOps & QA"),
        ("ACT-24", "4.3", "End-to-End Validation", "Execute 50 synthetic incident scenarios; evaluate patch compile & pass rate.", "ACT-22", "8", "Full Team"),
        ("ACT-25", "1.7", "Final Project Acceptance", "Compile comprehensive evaluation report, video demo, and sponsor sign-off.", "ACT-24", "4", "Project Manager")
    ]

    for item in activities:
        row = table.add_row()
        for idx, text in enumerate(item):
            c = row.cells[idx]
            c.width = col_widths[idx]
            p = c.paragraphs[0]
            p.text = text
            p.runs[0].font.size = Pt(8.5)
            set_cell_margins(c, 60, 60, 60, 60)
            if idx in [0, 1, 4, 5]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if idx == 0:
                p.runs[0].font.bold = True

    doc_path = os.path.join(OUT_DIR, "Activity_List_SPM.docx")
    doc.save(doc_path)
    print("Activity List docx generated!")

# ==========================================
# 5. GENERATE TOOLS USED DOCUMENT (.DOCX)
# ==========================================
def generate_tools_used():
    doc = base_doc()

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_t.add_run("TOOLS USED FOR WBS AND ACTIVITY LIST")
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Course: Software Project Management • Deliverable 3: Tools Justification Report\nStudent: Cătălinoiu Luis-Roberto (CTI English)  |  Coordinator: Ș.l. dr. ing. Ionuț Murarețu")
    r_sub.font.size = Pt(9.5)
    r_sub.italic = True
    r_sub.font.color.rgb = MUTED

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.font.size = Pt(13)
        r.bold = True
        r.font.color.rgb = NAVY
        return h

    def add_bullet(bold_pfx, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r_b = p.add_run(bold_pfx)
        r_b.bold = True
        p.add_run(text)
        return p

    add_h1("1. Overview of Tools Used")
    doc.add_paragraph(
        "To satisfy the academic requirements of Software Project Management (SPM) and adhere to professional industry standards "
        "(PMI / PMBOK and Agile frameworks), a hybrid suite of modern project engineering and diagramming tools was utilized to "
        "model the Work Breakdown Structure (WBS) and construct the Activity List."
    )

    add_h1("2. Tools Employed for the Work Breakdown Structure (WBS) Diagram")
    add_bullet("Draw.io (diagrams.net) & Python Matplotlib Engine: ", 
               "Used to construct the hierarchical, tree-structured graphical WBS diagram. Draw.io allowed rapid visual drafting "
               "of the multi-level decomposition (Root -> Level 1 Major Work Packages -> Level 2 Deliverables). To guarantee pixel-perfect "
               "vector resolution and exact formatting matching course templates, an automated rendering script was compiled to generate high-resolution PNG outputs.")
    add_bullet("Mermaid.js Diagramming Notation: ", 
               "Employed during initial architectural planning to maintain plain-text, version-controlled WBS definitions directly within project Markdown files on GitHub, ensuring traceability alongside source code.")

    add_h1("3. Tools Employed for the Activity List & Scheduling")
    add_bullet("Atlassian Jira Software (Cloud Agile Management): ", 
               "Jira was selected as the enterprise backbone for defining work activities. The WBS Level 1 packages were mapped directly into Jira EPICS, "
               "while Level 2 deliverables and specific activities were configured as USER STORIES and SUB-TASKS. Jira allowed exact specification of activity IDs, "
               "predecessor dependencies, time estimations (story points and calendar days), and assignment to specific team member roles (DevOps Engineer, ML Specialist, Backend Developer, QA).")
    add_bullet("Microsoft Word (python-docx Engine): ", 
               "Utilized to format the formal tabular Activity List deliverable. It provides structured columns for Activity ID, WBS Code, Task Name, Description, Predecessors, Duration, and Assigned Resource with shaded header rows and clean visual margins.")

    add_h1("4. Summary Comparison of Selected Tools")
    table = doc.add_table(rows=5, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Tool Name", "Artifact Created", "Key Capability", "Why Selected"]
    for idx, text in enumerate(headers):
        c = table.rows[0].cells[idx]
        p = c.paragraphs[0]
        p.text = text
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.color.rgb = NAVY
        set_cell_background(c, "EAECEE")
        set_cell_margins(c, 80, 80, 80, 80)

    data = [
        ("Draw.io / Matplotlib", "WBS Diagram (.png)", "Hierarchical tree rendering", "Visual clarity, exact adherence to faculty diagram format"),
        ("Atlassian Jira", "Agile Epics & Stories", "Sprint tracking & role allocation", "Industry-standard agile task assignment and dependency mapping"),
        ("Microsoft Word / docx", "Formal Documentation", "Structured tables & document layout", "Compliant academic document formatting"),
        ("GitHub Projects", "Issue Traceability", "Commit-to-task linking", "Continuous traceability from requirements to source code")
    ]

    for r_idx, vals in enumerate(data, start=1):
        row = table.rows[r_idx]
        for c_idx, val in enumerate(vals):
            c = row.cells[c_idx]
            p = c.paragraphs[0]
            p.text = val
            p.runs[0].font.size = Pt(9)
            set_cell_margins(c, 60, 60, 60, 60)
            if c_idx == 0:
                p.runs[0].font.bold = True

    doc_path = os.path.join(OUT_DIR, "Tools_Used_SPM.docx")
    doc.save(doc_path)
    print("Tools Used docx generated!")

if __name__ == '__main__':
    print("Starting generation...")
    generate_wbs_image()
    generate_project_charter()
    generate_scope_statement()
    generate_activity_list()
    generate_tools_used()
    print("All SPM deliverables successfully created in:", OUT_DIR)
