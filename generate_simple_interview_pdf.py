"""
Script to generate the Beginner-Friendly, Plain-English Interview Guide PDF
for the AI Finance Controller project.
Designed so that ANY person with zero coding knowledge can easily understand it.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header on later pages
        if self._pageNumber > 1:
            self.drawString(36, 812, "AI Finance Controller — Easy Interview Guide (Plain English Edition)")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.8)
            self.line(36, 804, 559, 804)
        
        # Footer
        self.setFont("Helvetica", 8)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 22, page_str)
        self.drawString(36, 22, "Prepared for Job Interviews • Simple & Easy to Explain")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.8)
        self.line(36, 32, 559, 32)
        self.restoreState()


def build_easy_pdf(filename="AI_Finance_Controller_Easy_Interview_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Palette
    c_primary = colors.HexColor("#1e3a8a")     # Deep Classic Navy
    c_accent = colors.HexColor("#0284c7")      # Bright Sky Blue
    c_green = colors.HexColor("#16a34a")       # Friendly Green
    c_dark = colors.HexColor("#1f2937")        # Charcoal text
    c_subtext = colors.HexColor("#4b5563")     # Subdued grey text
    c_bg_card = colors.HexColor("#f8fafc")     # Light card background
    c_border = colors.HexColor("#cbd5e1")      # Soft border
    c_highlight = colors.HexColor("#eff6ff")   # Soft blue card background
    c_amber = colors.HexColor("#b45309")

    # Typography styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        leftIndent=12,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_primary,
        spaceAfter=0
    )

    script_style = ParagraphStyle(
        'Script',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=0
    )

    q_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=5
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    td_bold = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    story = []

    # ==========================
    # HEADER / TITLE BLOCK
    # ==========================
    story.append(Paragraph("AI Finance Controller", title_style))
    story.append(Paragraph("Simple & Easy Interview Guide (Explained for Anyone Without a Technical Background)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Welcome Card
    welcome_text = (
        "<b>What is this document?</b> This guide explains your project in <b>simple, everyday English</b>. "
        "Whether you are talking to an HR recruiter, a manager, or a technical interviewer, you will be able to clearly explain "
        "<b>what the project does, why it matters, which tools were used (with easy real-life examples),</b> and exactly "
        "<b>what to say word-for-word</b> to ace your interview!"
    )
    welcome_box = Table([[Paragraph(welcome_text, callout_style)]], colWidths=[523])
    welcome_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_highlight),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(welcome_box)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 1: THE PURPOSE OF THE PROJECT (SIMPLE STORY)
    # ==========================
    story.append(Paragraph("1. What is the Purpose of This Project? (The Everyday Story)", h1_style))
    story.append(Paragraph(
        "To understand this project, imagine buying a product online for <b>$100</b>. In the real world, three different records are created:",
        body_style
    ))
    story.append(Paragraph("1. <b>The Website Ledger:</b> Says <i>'Customer paid $100 for an order'</i>.", bullet_style))
    story.append(Paragraph("2. <b>The Payment App (like Stripe or Razorpay):</b> Takes a $2 fee and records <i>'$98 received'</i>.", bullet_style))
    story.append(Paragraph("3. <b>The Bank Statement:</b> Shows <i>'$98 deposited into the company account'</i>.", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>The Real-World Problem:</b> When a company does thousands of transactions daily across different countries, "
        "currencies, and banks, these three records frequently <b>do not match!</b> "
        "A bank might charge a hidden fee, a customer might cancel at the exact same second, or currency rates might shift. "
        "Traditionally, human accountants have to sit with giant Excel sheets for weeks, comparing rows one by one to find missing money. "
        "It is slow, stressful, and mistakes cost companies millions of dollars.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution (Our Project):</b> We built a <b>smart AI Financial Controller</b> that acts like a 24/7 digital senior accountant. "
        "It automatically compares all three records in seconds, spots any missing money or mistakes, explains why the difference happened, "
        "and either fixes it automatically using company rules or alerts a human manager for high-value cases.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 2: HOW IT WORKS IN 3 SIMPLE STEPS
    # ==========================
    story.append(Paragraph("2. How Does It Work? (The 3-Step Magic)", h1_style))

    steps_data = [
        [
            Paragraph("Step 1: Check & Match", td_bold),
            Paragraph("The system reads thousands of transactions at once. It checks: <i>Did the bank receive what the website sold?</i> If yes, it marks it green (Balanced).", td_style)
        ],
        [
            Paragraph("Step 2: Detect & Investigate", td_bold),
            Paragraph("If there is a difference (e.g. $10 missing or an unusual gateway fee), the system catches it instantly and hands it to the built-in AI accountant to find the cause.", td_style)
        ],
        [
            Paragraph("Step 3: Resolve & Record", td_bold),
            Paragraph("If the difference is permitted by company policy (e.g. normal 2% foreign exchange fee), it resolves it automatically. If it looks suspicious, it alerts a human. Everything is saved in a permanent history log that nobody can tamper with.", td_style)
        ]
    ]
    steps_table = Table(steps_data, colWidths=[130, 393])
    steps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(steps_table)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 3: TOOLS & TECHNOLOGIES (WITH REAL-LIFE ANALOGIES)
    # ==========================
    story.append(PageBreak())
    story.append(Paragraph("3. Tools & Technologies Used (Explained with Everyday Analogies)", h1_style))
    story.append(Paragraph(
        "Here is the simple, non-technical explanation of every tool used in the project, so you can easily describe them to anyone:",
        body_style
    ))

    tools_data = [
        [Paragraph("Tool / Tech", th_style), Paragraph("Everyday Analogy", th_style), Paragraph("What it Does in This Project", th_style)],
        
        [
            Paragraph("<b>Python</b>", td_bold),
            Paragraph("The Brain / Engine", td_style),
            Paragraph("The main programming language doing the heavy calculations, comparing balances, and managing all logic.", td_style)
        ],
        [
            Paragraph("<b>FastAPI</b>", td_bold),
            Paragraph("The Restaurant Waiter", td_style),
            Paragraph("Takes orders from the user's screen, runs to the backend engine to get answers, and brings them back in milliseconds.", td_style)
        ],
        [
            Paragraph("<b>Google Gemini AI</b><br/>(Gemini 3.5)", td_bold),
            Paragraph("The Smart Digital Accountant", td_style),
            Paragraph("The intelligent assistant you chat with. It understands questions in plain English, calculates foreign exchange rates, and explains errors.", td_style)
        ],
        [
            Paragraph("<b>OpenRouter AI</b><br/>(Backup Engine)", td_bold),
            Paragraph("The Spare Tire", td_style),
            Paragraph("If Google's service is temporarily busy or reaches a daily limit, the system instantly switches to this backup AI with zero downtime.", td_style)
        ],
        [
            Paragraph("<b>RAG Policy Engine</b><br/>(Vector Store)", td_bold),
            Paragraph("The Company Rulebook", td_style),
            Paragraph("Stores the company's financial rules. When the AI speaks, it quotes exact policy rules (e.g. fee limits), preventing the AI from guessing or making up numbers.", td_style)
        ],
        [
            Paragraph("<b>HTML, CSS & JavaScript</b>", td_bold),
            Paragraph("The Modern Control Dashboard", td_style),
            Paragraph("Everything the user sees and clicks on their screen: the 10 navigation tabs, buttons, clean dark-mode visuals, and live chat drawer.", td_style)
        ],
        [
            Paragraph("<b>Chart.js</b>", td_bold),
            Paragraph("The Visual Storyteller", td_style),
            Paragraph("Turns dry numbers into colorful interactive charts, pie graphs, and progress bars so managers can see health at a glance.", td_style)
        ],
        [
            Paragraph("<b>Render Cloud</b>", td_bold),
            Paragraph("The 24/7 Powerhouse", td_style),
            Paragraph("Hosts both the website and backend online on the cloud, so anyone around the world can open the link anytime on their phone or laptop.", td_style)
        ],
        [
            Paragraph("<b>Vercel CDN</b>", td_bold),
            Paragraph("The Global Delivery Network", td_style),
            Paragraph("Distributes the frontend website worldwide for blazing-fast loading speeds no matter what country you open it from.", td_style)
        ]
    ]

    tools_table = Table(tools_data, colWidths=[105, 120, 298])
    tools_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_card]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tools_table)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 4: EXACT INTERVIEW TALKING SCRIPTS
    # ==========================
    story.append(Paragraph("4. Exactly What to Say in an Interview (Word-for-Word Scripts)", h1_style))
    story.append(Paragraph(
        "Memorize or adapt these two simple scripts depending on how much time you have:",
        body_style
    ))

    # 30-Second Pitch Box
    pitch_30 = (
        "<b>When the interviewer says: 'Give me a 30-second summary of your project':</b><br/>"
        "<i>\"I built an <b>AI Finance Controller</b> that solves one of the biggest headaches in business: <b>reconciliation</b>. "
        "When companies process thousands of payments across Stripe, PayPal, and banks, the numbers often don't match due to currency fees or timing delays. "
        "Instead of humans spending weeks on Excel sheets, my platform automatically compares thousands of transactions in seconds, "
        "uses Google Gemini AI to investigate any missing money, applies official corporate rules to resolve them, and provides a 24/7 interactive chat copilot for the finance team.\"</i>"
    )
    p30_box = Table([[Paragraph(pitch_30, script_style)]], colWidths=[523])
    p30_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ]))
    story.append(p30_box)
    story.append(Spacer(1, 8))

    # 2-Minute Detailed Pitch Box
    pitch_2min = (
        "<b>When the interviewer says: 'Tell me about the architecture and how you built it':</b><br/>"
        "<i>\"The system has three main parts working together:<br/>"
        "1. <b>The Backend Engine:</b> Built with Python and FastAPI. It runs high-speed matching algorithms that compare payments across banks and gateways.<br/>"
        "2. <b>The AI Brain:</b> Powered by Google's Gemini 3.5 AI, backed by a backup AI on OpenRouter. If an anomaly is found—like an unexpected fee on a $2,000 USD transfer—the AI reads our company's policy rulebook, calculates the exact fee in INR, and explains the discrepancy in plain English.<br/>"
        "3. <b>The User Interface:</b> A responsive, dark-mode dashboard built with JavaScript and Chart.js. Finance managers can view real-time charts, click into discrepancies, or chat with the AI Copilot just like ChatGPT for finance.<br/>"
        "Everything is live and hosted on Render Cloud and Vercel for public access.\"</i>"
    )
    p2min_box = Table([[Paragraph(pitch_2min, script_style)]], colWidths=[523])
    p2min_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ]))
    story.append(p2min_box)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 5: COMMON INTERVIEW QUESTIONS (EASY ANSWERS)
    # ==========================
    story.append(PageBreak())
    story.append(Paragraph("5. Top Interview Questions & Simple Answers Anyone Can Give", h1_style))
    story.append(Paragraph(
        "Here are the questions interviewers love to ask, and the simplest ways to answer them with confidence:",
        body_style
    ))

    faq = [
        ("Q1: Why did you use AI? Why not just use standard computer code?",
         "<b>How to answer:</b> <i>\"Standard code is great at simple math like 10 minus 2 equals 8. But standard code cannot understand <b>context</b>. "
         "For example, if a payment is delayed because of a holiday in Germany, or if a customer claims they were charged twice, traditional code just throws an error. "
         "The AI acts like an experienced human investigator: it reads notes, checks foreign currency rates, references policy documents, and writes a clear explanation for the team.\"</i>"),
        
        ("Q2: In finance, mistakes are dangerous. What if the AI makes up a wrong number (hallucinates)?",
         "<b>How to answer:</b> <i>\"That was our number one safety priority! We protected against this in three ways:<br/>"
         "• <b>First, the AI doesn't do the raw math in its head:</b> Python code calculates all the actual dollar and rupee totals deterministically. The AI only summarizes and explains the results.<br/>"
         "• <b>Second, we give it the rulebook:</b> It must cite an official policy rule before recommending any adjustment.<br/>"
         "• <b>Third, human approval:</b> Small, expected fee differences auto-clear, but any large or unusual difference is locked until a human manager clicks 'Approve'.\"</i>"),

        ("Q3: What happens if the AI service goes down or runs out of credits?",
         "<b>How to answer:</b> <i>\"We designed a zero-downtime safety net! If Google Gemini is busy or reaches its limit, the system automatically redirects the question to our backup AI engine (OpenRouter) in less than a second. If the internet completely drops, the system falls back to built-in rule calculations. The user never sees a broken screen.\"</i>"),

        ("Q4: Can you explain how you handled different currencies (like USD to Indian Rupee)?",
         "<b>How to answer:</b> <i>\"Yes! When money travels across borders, two things happen: the exchange rate changes, and the payment gateway takes a processing fee. "
         "Our system takes the transaction amount, applies the official exchange rate (like 1 USD = ₹86.50), deducts the allowed 2.5% gateway fee according to company policy, "
         "and verifies that the final amount arriving in the bank account matches down to the exact cent.\"</i>"),

        ("Q5: What was the most challenging part of this project, and how did you solve it?",
         "<b>How to answer:</b> <i>\"The biggest challenge was making sure the AI gave accurate, structured financial answers without getting confused by technical jargon. "
         "I solved this by creating a prompt engineering framework that gives the AI a clear role as a 'Senior Finance Controller', feeds it the relevant policy guidelines, "
         "and connects it directly to real-time calculation tools.\"</i>")
    ]

    for q, a in faq:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a, ans_style))
        story.append(Spacer(1, 4))

    # ==========================
    # SECTION 6: KEY FEATURES YOU CAN DEMO LIVE
    # ==========================
    story.append(Spacer(1, 6))
    story.append(Paragraph("6. Key Features You Can Show or Mention in the Demo", h1_style))

    features = [
        "<b>1. Live AI Copilot Drawer:</b> A floating chat assistant where you can type questions like <i>'Convert 1,000 USD to INR with gateway fees'</i> and receive a live breakdown.",
        "<b>2. Tri-Way Reconciliation Table:</b> A color-coded table showing green for balanced transactions and red for discrepancies that need attention.",
        "<b>3. Automated Dispute Resolution:</b> Clicking 'Investigate' triggers the AI to explain the root cause and recommend the exact journal adjustment.",
        "<b>4. Interactive Health & Metric Charts:</b> Visual graphs showing how many thousands of dollars were saved and the percentage of auto-reconciled items.",
        "<b>5. Live Cloud Deployment:</b> It is not just running on your laptop; it is hosted live online at Render and Vercel for anyone to test."
    ]
    for f in features:
        story.append(Paragraph(f"• {f}", bullet_style))

    story.append(Spacer(1, 10))

    # Quick Summary Card
    concl_text = (
        "<b>Final Interview Tip:</b> Keep your tone confident and focus on the <b>business value</b>! "
        "Companies love candidates who don't just write code, but understand how technology saves time, cuts costs, and prevents human errors. "
        "Highlighting that this project saves accounting teams hundreds of hours each month will make you stand out from other candidates!"
    )
    concl_box = Table([[Paragraph(concl_text, callout_style)]], colWidths=[523])
    concl_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#fcd34d")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(concl_box)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Plain-English PDF generated: {filename}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "AI_Finance_Controller_Easy_Interview_Guide.pdf"
    build_easy_pdf(out_file)
