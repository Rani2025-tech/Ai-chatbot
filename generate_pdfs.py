from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT_DIR = "data"

def make_pdf(filename, title, sections):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=18, spaceAfter=16, alignment=TA_CENTER)
    heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=6)

    story = [Paragraph(title, title_style), Spacer(1, 0.2 * inch)]
    for heading, lines in sections:
        story.append(Paragraph(heading, heading_style))
        for line in lines:
            story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    print(f"Created: {path}")


# ── 1. ADMISSIONS ────────────────────────────────────────────────
make_pdf("nist_admissions.pdf", "NIST University — Admissions Guide", [
    ("About NIST University", [
        "National Institute of Science and Technology (NIST University) is a premier private engineering institution located at Institute Park, Pallur Hills, Berhampur, Odisha - 761008, India.",
        "Established with a vision to provide world-class technical education, NIST is approved by AICTE and affiliated to Biju Patnaik University of Technology (BPUT), Odisha.",
    ]),
    ("Eligibility Criteria for B.Tech", [
        "Candidates must have passed 10+2 (Class XII) or equivalent examination with Physics, Chemistry, and Mathematics (PCM) as core subjects.",
        "Minimum aggregate of 45% marks in PCM for General category and 40% for SC/ST candidates.",
        "Candidates must have appeared in JEE Main or OJEE entrance examination.",
    ]),
    ("Admission Process", [
        "Step 1: Appear in JEE Main (conducted by NTA) or OJEE (Odisha Joint Entrance Examination).",
        "Step 2: Register on the NIST University official admissions portal with your JEE/OJEE rank and personal details.",
        "Step 3: Attend OJEE counselling — 70% of B.Tech seats are filled through OJEE counselling rounds.",
        "Step 4: Management Quota — 15% of seats are reserved under Management/NRI Sponsored category, filled directly by the institute.",
        "Step 5: Submit original documents for verification: Class X & XII marksheets, JEE/OJEE scorecard, category certificate (if applicable), passport-size photographs.",
        "Step 6: Pay the admission fee to confirm your seat.",
    ]),
    ("Seat Distribution", [
        "OJEE Counselling Seats: 70% of total intake.",
        "Management Quota Seats: 15% of total intake.",
        "NRI Sponsored Category: 15% of total intake.",
        "Total intake varies by branch — CSE and ECE have the highest intake.",
    ]),
    ("Important Documents Required", [
        "Class X Board Marksheet and Certificate.",
        "Class XII Board Marksheet and Certificate.",
        "JEE Main Scorecard or OJEE Rank Card.",
        "Transfer Certificate (TC) from previous institution.",
        "Character Certificate.",
        "Category/Caste Certificate (for SC/ST/OBC candidates).",
        "Passport-size photographs (6 copies).",
        "Aadhaar Card.",
    ]),
    ("Contact for Admissions", [
        "Address: Institute Park, Pallur Hills, Berhampur, Odisha - 761008.",
        "Website: www.nist.edu",
        "Admissions Helpline: Available on the official NIST University website.",
    ]),
])

# ── 2. FEES ──────────────────────────────────────────────────────
make_pdf("nist_fees.pdf", "NIST University — Fee Structure", [
    ("B.Tech Tuition Fee — Branch Wise", [
        "The total B.Tech program fee for 4 years ranges from approximately Rs 5.1 Lakh to Rs 7.02 Lakh depending on the branch.",
        "CSE (Computer Science and Engineering): Approximately Rs 1.75 Lakh per year, Rs 7.02 Lakh for 4 years.",
        "IT (Information Technology): Approximately Rs 1.75 Lakh per year, Rs 7.02 Lakh for 4 years.",
        "CSE with AI & ML specialization: Approximately Rs 1.75 Lakh per year, Rs 7.02 Lakh for 4 years.",
        "CSE with Data Science specialization: Approximately Rs 1.75 Lakh per year, Rs 7.02 Lakh for 4 years.",
        "ECE (Electronics and Communication Engineering): Approximately Rs 1.5 Lakh per year, Rs 6.0 Lakh for 4 years.",
        "EEE (Electrical and Electronics Engineering): Approximately Rs 1.4 Lakh per year, Rs 5.6 Lakh for 4 years.",
        "Civil Engineering: Approximately Rs 1.27 Lakh per year, Rs 5.1 Lakh for 4 years.",
        "Mechanical Engineering: Approximately Rs 1.27 Lakh per year, Rs 5.1 Lakh for 4 years.",
        "Fees are paid semester-wise (2 semesters per year).",
        "Approximate per-semester tuition fee: Rs 63,750 to Rs 87,750 per semester depending on branch.",
    ]),
    ("Postgraduate Fee Structure", [
        "MBA (Master of Business Administration): Approximately Rs 1.5 Lakh to Rs 1.8 Lakh per year, Rs 3.0 Lakh to Rs 3.6 Lakh for 2 years.",
        "MCA (Master of Computer Applications): Approximately Rs 1.4 Lakh to Rs 1.6 Lakh per year, Rs 2.8 Lakh to Rs 3.2 Lakh for 2 years.",
        "M.Tech: Approximately Rs 1.2 Lakh to Rs 1.5 Lakh per year, Rs 2.4 Lakh to Rs 3.0 Lakh for 2 years.",
    ]),
    ("Hostel Fee Structure", [
        "NIST University provides on-campus residential facilities for both boys and girls separately.",
        "Non-AC Room: Rs 35,000 to Rs 40,000 per year.",
        "AC Room: Rs 53,000 to Rs 60,000 per year.",
        "Hostel fees include accommodation charges, electricity (limited units), and basic amenities.",
        "Hostel fee is paid annually at the beginning of each academic year.",
    ]),
    ("Mess / Dining Charges", [
        "Mess charges are approximately Rs 4,500 to Rs 5,000 per month.",
        "Annual mess charges: approximately Rs 54,000 to Rs 60,000 per year.",
        "The mess provides vegetarian and non-vegetarian meals with a monthly menu rotation.",
        "Students can opt in or out of the mess facility each semester.",
    ]),
    ("Other Fees", [
        "Examination Fee: Charged per semester as per university norms.",
        "Library Fee: Included in the annual academic fee.",
        "Lab Fee: Included in the semester fee for respective branches.",
        "Development Fee: One-time fee paid at the time of admission.",
        "Caution Deposit: Refundable deposit collected at admission, approximately Rs 10,000 to Rs 15,000.",
    ]),
    ("Total Estimated Annual Cost", [
        "Tuition Fee for CSE/IT per year: Rs 1.75 Lakh approximately.",
        "Tuition Fee for Civil/Mechanical per year: Rs 1.27 Lakh approximately.",
        "Hostel Fee (Non-AC) per year: Rs 35,000 to Rs 40,000.",
        "Hostel Fee (AC) per year: Rs 53,000 to Rs 60,000.",
        "Mess Charges per year: Rs 54,000 to Rs 60,000.",
        "Total estimated annual cost for CSE with Non-AC hostel: Rs 2.66 Lakh to Rs 2.75 Lakh approximately.",
        "Total estimated annual cost for Civil/Mechanical with Non-AC hostel: Rs 2.16 Lakh to Rs 2.27 Lakh approximately.",
    ]),
    ("Fee Payment", [
        "Fees can be paid online via the NIST student portal using Net Banking, UPI, or Debit/Credit Card.",
        "Offline payment via Demand Draft (DD) is also accepted at the accounts office.",
        "Late fee penalty is applicable if fees are not paid within the due date.",
    ]),
])

# ── 3. COURSES ───────────────────────────────────────────────────
make_pdf("nist_courses.pdf", "NIST University — Courses Offered", [
    ("Undergraduate Programs (B.Tech)", [
        "Duration: 4 years (8 semesters).",
        "1. Computer Science and Engineering (CSE)",
        "2. Information Technology (IT)",
        "3. Electronics and Communication Engineering (ECE)",
        "4. Electrical and Electronics Engineering (EEE)",
        "5. Civil Engineering",
        "6. Mechanical Engineering",
        "7. CSE with specialization in Artificial Intelligence and Machine Learning (AI & ML)",
        "8. CSE with specialization in Data Science",
    ]),
    ("Postgraduate Programs", [
        "M.Tech: Available in various specializations including Computer Science, VLSI Design, Power Systems, and Structural Engineering. Duration: 2 years.",
        "MBA: Master of Business Administration with specializations in Finance and Human Resource Management. Duration: 2 years.",
        "MCA: Master of Computer Applications. Duration: 2 years.",
    ]),
    ("CSE Specializations (AI & ML, Data Science)", [
        "The AI & ML specialization covers Machine Learning, Deep Learning, Natural Language Processing, Computer Vision, and Robotics.",
        "The Data Science specialization covers Big Data Analytics, Data Visualization, Statistical Modelling, Python for Data Science, and Cloud Computing.",
        "Both specializations have dedicated labs and industry-aligned curriculum.",
    ]),
    ("Key Subjects in B.Tech CSE", [
        "Semester 1-2: Engineering Mathematics, Physics, Chemistry, Basic Electrical Engineering, Programming in C.",
        "Semester 3-4: Data Structures, Object Oriented Programming (Java), Database Management Systems, Computer Organization.",
        "Semester 5-6: Operating Systems, Computer Networks, Software Engineering, Machine Learning, Web Technologies.",
        "Semester 7-8: Cloud Computing, Artificial Intelligence, Project Work, Electives.",
    ]),
    ("Affiliated University & Approvals", [
        "NIST University is affiliated to Biju Patnaik University of Technology (BPUT), Odisha.",
        "Approved by All India Council for Technical Education (AICTE), New Delhi.",
        "Recognized by the University Grants Commission (UGC).",
    ]),
])

# ── 4. PLACEMENTS ────────────────────────────────────────────────
make_pdf("nist_placements.pdf", "NIST University — Placements", [
    ("Placement Overview", [
        "NIST University has a dedicated Training and Placement Cell that facilitates campus recruitment for final year students.",
        "Placement rate: Over 60% to 70% of eligible students receive campus placement offers every year.",
        "The placement cell provides pre-placement training including aptitude, technical, and soft skills preparation.",
    ]),
    ("2025 Batch Placement Stats", [
        "Total offers extended: Over 280 offers as of March 2025.",
        "Number of recruiters: 82+ companies visited campus for the 2025 batch.",
        "Highest package (2025 batch): ₹23 LPA to ₹28 LPA (historically recorded).",
        "Average package (2025 batch): ₹4 LPA to ₹6 LPA.",
    ]),
    ("2024 Batch Placement Stats", [
        "Highest package (2024 batch): ₹12 LPA.",
        "Average package (2024 batch): ₹5 LPA.",
        "CSE and IT branches had the highest placement percentage.",
    ]),
    ("Top Recruiting Companies", [
        "IT & Software: Infosys, Wipro, TCS, Cognizant, Accenture, Amazon, Tech Mahindra, HCL Technologies.",
        "Core Engineering: L&T, TATA Motors, Bosch, Siemens.",
        "Analytics & Consulting: Deloitte, Capgemini, IBM.",
        "Startups & Product Companies: Various funded startups and product-based companies also recruit from NIST.",
    ]),
    ("Pre-Placement Training", [
        "The Training and Placement Cell conducts year-round training from 2nd year onwards.",
        "Aptitude Training: Quantitative, Logical Reasoning, Verbal Ability.",
        "Technical Training: Data Structures, Algorithms, DBMS, OS, Networking.",
        "Soft Skills: Communication, Group Discussion, Mock Interviews.",
        "Coding Platforms: Students are trained on HackerRank, LeetCode, and CodeChef.",
    ]),
    ("Internships", [
        "NIST encourages students to pursue internships after 2nd and 3rd year.",
        "Many students secure internships at TCS, Infosys, and local IT companies.",
        "Internship opportunities are also posted through the placement cell portal.",
    ]),
])

# ── 5. CAMPUS ────────────────────────────────────────────────────
make_pdf("nist_campus.pdf", "NIST University — Campus & Facilities", [
    ("Campus Overview", [
        "NIST University is situated at Institute Park, Pallur Hills, Berhampur, Odisha - 761008.",
        "The campus spans approximately 60 to 65 acres amidst the scenic Pallur Hills.",
        "The campus has a green, pollution-free environment with modern infrastructure.",
    ]),
    ("Academic Infrastructure", [
        "Well-equipped classrooms with projectors and smart boards.",
        "Dedicated department buildings for each engineering branch.",
        "Seminar halls and auditoriums for events and conferences.",
        "Central computerized library with a vast collection of textbooks, international journals, and e-resources.",
    ]),
    ("Specialised Labs & Research Centres", [
        "AI & Robotics Lab: Includes a 3D Printing & Robotics Lab and an Autonomous Formulation Lab (AFL) that integrates AI with robotic platforms.",
        "IBM Centre for Excellence: Industry collaboration lab for software and cloud technologies.",
        "CISCO Networking Lab: Advanced networking lab for ECE and CSE students.",
        "Cloud Computing Lab: Hands-on training on AWS, Azure, and Google Cloud.",
        "Nanotechnology Lab: Research-focused lab for advanced material science.",
        "VLSI Design Lab: Dedicated lab for electronics and chip design.",
    ]),
    ("Hostel Facilities", [
        "Separate hostel buildings for boys and girls on campus.",
        "Non-AC and AC room options available.",
        "24-hour security and CCTV surveillance.",
        "Common rooms, reading rooms, and indoor recreation facilities in hostels.",
        "Wi-Fi connectivity available in all hostel buildings.",
    ]),
    ("Sports & Recreation", [
        "Semi-Olympic sized swimming pool.",
        "Indoor stadium for badminton, table tennis, and other indoor sports.",
        "Gymnasium with modern fitness equipment.",
        "Basketball court, Volleyball court, and Lawn Tennis court.",
        "Open grounds for cricket and football.",
    ]),
    ("Other Facilities", [
        "Wi-Fi: The entire campus is Wi-Fi enabled with high-speed internet in academic buildings and hostels.",
        "Canteen & Mess: Multiple canteens and a central mess serving hygienic food.",
        "Medical Centre: On-campus health centre with a resident doctor.",
        "Bank & ATM: ATM facility available on campus.",
        "Transport: Bus facility available for day scholars from Berhampur city.",
    ]),
])

# ── 6. ACADEMICS ─────────────────────────────────────────────────
make_pdf("nist_academics.pdf", "NIST University — Academics & Examination", [
    ("Academic Structure", [
        "B.Tech program follows a semester system with 8 semesters over 4 years.",
        "Each academic year consists of 2 semesters: Odd Semester (July to November) and Even Semester (December to April).",
        "Each semester has approximately 90 working days of instruction.",
    ]),
    ("Examination Pattern", [
        "Each subject is evaluated for 100 marks total.",
        "Internal Assessment (IA): 30 marks — includes mid-semester tests, assignments, lab performance, and attendance.",
        "End Semester Examination (ESE): 70 marks — conducted by BPUT at the end of each semester.",
        "Pass mark: Minimum 40 out of 100 (combined internal + external).",
        "Minimum pass mark in End Semester Exam: 28 out of 70.",
    ]),
    ("Grading System", [
        "NIST follows the CGPA (Cumulative Grade Point Average) system as per BPUT norms.",
        "Grade O (Outstanding): 90-100 marks — 10 grade points.",
        "Grade E (Excellent): 80-89 marks — 9 grade points.",
        "Grade A (Very Good): 70-79 marks — 8 grade points.",
        "Grade B (Good): 60-69 marks — 7 grade points.",
        "Grade C (Average): 50-59 marks — 6 grade points.",
        "Grade D (Pass): 40-49 marks — 5 grade points.",
        "Grade F (Fail): Below 40 marks — 0 grade points.",
    ]),
    ("Attendance Rules", [
        "Minimum attendance requirement: 75% in each subject per semester.",
        "Students with attendance below 75% are not allowed to appear in the End Semester Examination.",
        "Medical leave is considered with proper documentation but attendance must still meet the minimum threshold.",
        "Condonation of attendance shortage may be granted in exceptional cases by the Principal.",
    ]),
    ("Backlog & Arrear Rules", [
        "Students who fail in a subject (below 40 marks) are considered to have a backlog/arrear in that subject.",
        "Backlog subjects can be cleared in subsequent semester examinations.",
        "Students must clear all backlogs to be eligible for the final semester examination and degree.",
        "A student cannot have more than a specified number of backlogs to be promoted to the next year.",
    ]),
    ("Project & Internship", [
        "7th and 8th semester include a major project (final year project) as a compulsory component.",
        "Students are encouraged to do internships during summer breaks after 2nd and 3rd year.",
        "Mini projects are assigned in 5th and 6th semester as part of the curriculum.",
    ]),
])

# ── 7. SCHOLARSHIPS ──────────────────────────────────────────────
make_pdf("nist_scholarships.pdf", "NIST University — Scholarships & Financial Aid", [
    ("Merit-Based Scholarships", [
        "NIST University offers merit-based scholarships to academically outstanding students.",
        "Eligibility: Students who secure top ranks in JEE Main or OJEE are eligible for fee waivers.",
        "Top OJEE rankers (within state rank 100) may receive significant tuition fee concessions.",
        "Students maintaining a CGPA of 8.5 and above in the previous semester are eligible for academic excellence scholarships.",
        "Merit scholarships are reviewed every semester based on academic performance.",
    ]),
    ("Government Scholarships", [
        "NIST accepts all State and Central Government scholarship schemes.",
        "Students must apply through the official government scholarship portals and submit proof of admission.",
    ]),
    ("PRERANA Scholarship (Odisha)", [
        "PRERANA is a State Government of Odisha scholarship scheme for meritorious students from economically weaker sections.",
        "Eligible students: SC, ST, OBC, and minority community students from Odisha.",
        "The scholarship covers a portion of tuition fees and is disbursed directly to the student's bank account.",
        "Students must apply through the official Odisha scholarship portal (scholarships.odisha.gov.in).",
        "Required documents: Income certificate, caste certificate, bank account details, admission proof.",
    ]),
    ("SC/ST Scholarships", [
        "SC and ST students are eligible for Post-Matric Scholarship under the Central Government scheme.",
        "The scholarship covers tuition fees, maintenance allowance, and other academic charges.",
        "Apply through the National Scholarship Portal (scholarships.gov.in).",
    ]),
    ("Minority Scholarships", [
        "Students from minority communities (Muslim, Christian, Sikh, Buddhist, Jain, Parsi) can apply for the Pre-Matric and Post-Matric Minority Scholarship.",
        "Administered by the Ministry of Minority Affairs, Government of India.",
        "Apply through the National Scholarship Portal (scholarships.gov.in).",
    ]),
    ("How to Apply for Scholarships", [
        "Step 1: Register on the National Scholarship Portal (scholarships.gov.in) or Odisha Scholarship Portal.",
        "Step 2: Fill in your personal, academic, and bank details.",
        "Step 3: Upload required documents: income certificate, caste certificate, marksheets, admission letter.",
        "Step 4: Submit the application before the deadline (usually October-November each year).",
        "Step 5: The institute verifies and approves the application.",
        "Step 6: Scholarship amount is disbursed directly to the student's bank account.",
    ]),
])

print("\n✅ All 7 PDFs generated successfully in the data/ folder!")
