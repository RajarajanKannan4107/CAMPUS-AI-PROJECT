# Install dependencies:
# pip install fastapi uvicorn sentence-transformers numpy groq python-dotenv
#
# Run server:
# uvicorn main:app --reload

import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()

SAMPLE_DATA = {
    "courses.txt": """B.Tech Computer Science and Engineering (CSE) at Greenfield Institute of Technology: The B.Tech in Computer Science and Engineering is a 4-year undergraduate program spanning 8 semesters with 160 credits. The tuition fee is $4,500 per semester. Eligibility requires at least 60% aggregate in 10+2 with Physics, Mathematics, and Chemistry. Core subjects include Data Structures, Algorithms, Operating Systems, Computer Networks, Database Management Systems, and Artificial Intelligence.

B.Tech Electronics and Communication Engineering (ECE) at Greenfield Institute of Technology: The B.Tech in Electronics and Communication Engineering is a 4-year program requiring 160 credits across 8 semesters. Tuition fee is $4,200 per semester. Eligibility requires 60% in 10+2 with Physics, Chemistry, and Mathematics. Core subjects include VLSI Design, Digital Signal Processing, Embedded Systems, Microprocessors, Analog Circuits, and Wireless Communications.

B.Tech Mechanical Engineering at Greenfield Institute of Technology: The B.Tech in Mechanical Engineering is a 4-year undergraduate degree requiring 160 credits. Tuition fee is $3,800 per semester. Eligibility requires 55% in 10+2 with Physics, Chemistry, and Mathematics. Core syllabus highlights include Thermodynamics, Fluid Mechanics, Kinematics, CAD/CAM, Heat Transfer, Manufacturing Technology, and Robotics.

B.Tech Civil Engineering at Greenfield Institute of Technology: The B.Tech in Civil Engineering is a 4-year degree spanning 8 semesters with 160 credits. Tuition fee is $3,600 per semester. Eligibility requires 55% in 10+2 with Physics, Chemistry, and Mathematics. The syllabus covers Structural Analysis, Geotechnical Engineering, Concrete Technology, Surveying, Transportation Engineering, and Environmental Engineering.

Master of Business Administration (MBA) at Greenfield Institute of Technology: The MBA is a 2-year postgraduate program consisting of 4 semesters and 96 credits. Tuition fee is $5,000 per semester. Eligibility requires a Bachelor's degree in any discipline with at least 50% marks and a valid score in GIT-MAT, CAT, or MAT. Specializations are offered in Finance, Marketing, Human Resource Management, and Business Analytics.

Professional and Open Electives in B.Tech Programs: Students at Greenfield Institute of Technology choose professional and open electives starting from the 5th semester. Elective courses account for 18 credits out of the 160 total credits. Popular electives include Machine Learning, Cloud Computing, Cybersecurity, Supply Chain Management, Internet of Things (IoT), and Green Architecture.

Honors and Minor Specializations at Greenfield Institute of Technology: High-performing B.Tech students with a CGPA of 8.0 or higher and no backlogs can earn an Honors degree in their branch or a Minor in another discipline (such as Minor in Computer Science or Minor in Data Science) by completing 18 additional credits between the 4th and 8th semesters.

Academic Credit Structure and 10-Point Grading System: Greenfield Institute of Technology adheres to a 10-point relative grading scale ranging from A+ (10 points) down to F (Fail, 0 points). To graduate, undergraduate students must successfully complete 160 credits with a minimum cumulative grade point average (CGPA) of 5.0. Postgraduate MBA students must complete 96 credits.

Internship Requirements and Capstone Senior Projects: All undergraduate students must complete a mandatory 8-week industrial summer internship after the 6th semester worth 2 credits. In the final year (7th and 8th semesters), students complete a two-phase Capstone Senior Project worth 8 credits under faculty mentorship.

Integrated Dual Degree (B.Tech + M.Tech) Program: Greenfield Institute of Technology offers a 5-year integrated dual degree program combining B.Tech and M.Tech in Computer Science and Electronics. The dual degree totals 210 credits with an annual tuition fee of $8,500. Eligibility requires a CGPA of 8.5 or higher at the end of the second year.""",

    "departments.txt": """Department of Computer Science and Engineering (CSE): Head of Department is Dr. Aris Thorne. Office location is Turing Block, Room 302. Official email is cse.hod@greenfield.edu, phone extension is 3101. HOD office hours are Monday through Thursday, 2:00 PM to 4:00 PM. Department administrative coordinator is in Room 301.

Department of Electronics and Communication Engineering (ECE): Head of Department is Dr. Elena Rostova. Office location is Faraday Hall, Room 215. Official email is ece.hod@greenfield.edu, phone extension is 3201. HOD office hours for student meetings are Tuesday and Thursday, 10:00 AM to 12:00 PM.

Department of Mechanical Engineering: Head of Department is Prof. Marcus Vance. Office location is Newton Complex, Room 104. Official email is mech.hod@greenfield.edu, phone extension is 3301. HOD office hours are Monday, Wednesday, and Friday, 11:00 AM to 1:00 PM.

Department of Civil Engineering: Head of Department is Dr. Sophia Lin. Office location is Smeaton Wing, Room 112. Official email is civil.hod@greenfield.edu, phone extension is 3401. HOD office hours are Tuesday and Friday, 2:30 PM to 4:30 PM.

Department of Management Studies (MBA): Head of Department is Dr. Rajiv Kapoor. Office location is Chanakya Block, Room 401. Official email is mba.hod@greenfield.edu, phone extension is 3501. HOD office hours are Monday through Friday, 3:00 PM to 5:00 PM.

Department of Basic Sciences and Humanities: Head of Department is Dr. Clara Oswald. Office location is Ramanujan Hall, Room 201. Official email is bsh.hod@greenfield.edu, phone extension is 3010. Office hours are Monday through Thursday, 9:30 AM to 11:30 AM. The department oversees first-year mathematics, physics, chemistry, and communications.

Office of the Dean of Academic Affairs: The Dean of Academic Affairs is Dr. Jonathan Briggs. Office location is Administrative Block, Room 101. Official email is dean.academics@greenfield.edu, phone extension is 1005. Office hours for student matters are Monday through Friday, 10:00 AM to 12:30 PM.

Office of the Dean of Student Affairs: The Dean of Student Affairs is Dr. Sarah Jenkins. Office location is Student Activity Center (SAC), Room 204. Official email is dean.studentwelfare@greenfield.edu, phone extension is 1008. Office hours are Monday through Friday, 3:00 PM to 5:00 PM.

Controller of Examinations (CoE) Office: The Controller of Examinations is Dr. Vikram Patel. Office location is Examination Center, Ground Floor. Official email is coe@greenfield.edu, phone extension is 1020. Office hours for grade sheets, verifications, and exam queries are Monday through Friday, 10:00 AM to 1:00 PM.

Office of Admissions and International Relations: The Director of Admissions is Prof. Miriam Chen. Office location is Gateway Building, Room G-05. Official email is admissions@greenfield.edu, phone extension is 1015. Office hours are Monday through Friday, 9:00 AM to 5:00 PM.""",

    "facilities.txt": """Central Library Timings and Borrowing Limits: The Central Library is open Monday to Saturday from 8:00 AM to 10:00 PM, and Sundays from 10:00 AM to 6:00 PM. During exam weeks, reading halls remain open 24/7. Undergraduate students can borrow up to 4 books for 14 days; postgraduate students can borrow 6 books for 30 days. Renewal is permitted once online. Late fee is $0.50 per day per book.

Computing Laboratories and Advanced Tech Centers: Greenfield Institute houses 8 air-conditioned computer labs in Turing Block with over 500 modern workstations running Windows and Ubuntu Linux. GPU clusters for machine learning and AI research are located in Lab 6. Computing labs are open daily from 8:30 AM to 8:30 PM.

Engineering Workshops and Maker Space: Fabrication, 3D printing, laser cutting, and robotics workshops are located in the Tech Park Building, Room 101. Material testing and civil labs are in Smeaton Wing. Open weekdays from 9:00 AM to 5:00 PM with technical supervisors on duty. Safety lab coats and goggles are strictly mandatory.

Campus Hostels and Accommodation: Greenfield Institute provides separate residential hostels: Pine Hall and Oak Hall for boys, and Maple Hall and Willow Hall for girls. Accommodations include single, double, and triple-occupancy rooms with Wi-Fi, laundry facilities, study halls, and backup power. Curfew is 9:30 PM on weekdays and 10:30 PM on weekends.

Cafeteria, Food Courts, and Dining Services: The Main Cafeteria in the Student Activity Center operates daily from 7:30 AM to 9:30 PM, serving nutritious vegetarian, non-vegetarian, vegan, and halal meals. A Nescafe coffee kiosk and Green Bites fresh juice bar near Turing Block operate until 11:00 PM.

Gymnasium and Fitness Center: The campus gym in the Sports Complex is equipped with cardio machines, free weights, resistance equipment, and certified trainers. Operating hours are 6:00 AM to 9:00 AM and 4:30 PM to 9:00 PM, Monday through Saturday. Gym access is completely free for enrolled students presenting their student ID card.

Sports Grounds and Outdoor Athletic Courts: Greenfield Institute features a standard 400-meter running track, a full-sized football ground, an illuminated cricket pitch, two basketball courts, and three indoor badminton courts. Sports gear can be checked out free of charge from the Sports Equipment Room between 4:00 PM and 8:00 PM daily.

Campus Wi-Fi Network (GIT-Secure): High-speed Wi-Fi network 'GIT-Secure' delivers 1 Gbps internet connectivity across all academic blocks, hostels, library, and cafeteria. Students log in using their student portal roll number and password. Device MAC address registration is handled online via git-wifi.greenfield.edu.

Campus Transport and Shuttle Bus Services: The institute operates 15 air-conditioned buses connecting the campus to metro stations and city neighborhoods. Morning pick-ups run between 7:45 AM and 8:15 AM, and evening drop-offs depart at 4:30 PM and 6:00 PM. Free electric golf-cart shuttles run between campus buildings every 15 minutes.

Auditorium and Seminar Halls: The Dr. APJ Kalam Central Auditorium accommodates 1,200 attendees with digital acoustic and stage lighting systems for college events, convocations, and festivals. Each academic building also contains two 150-seat air-conditioned seminar halls for guest lectures and conferences.""",

    "academic_procedures.txt": """Bonafide Certificate Application Procedure: To apply for a Bonafide Certificate for passport, visa, education loan, or transit pass purposes, submit a request via the Student Portal (portal.greenfield.edu > Certificates). Application fee is $5 paid online. Processing takes 2 business days. Collect the stamped physical certificate from Administrative Block Room 102 or download a verified digital copy.

Official Transcript Request Process and Fees: Official academic transcripts can be ordered through portal.greenfield.edu/transcripts or in person at Registrar Counter 2. Standard fee is $15 per transcript set for domestic delivery and $35 for international courier dispatch. Standard processing takes 5 to 7 business days. An expedited 24-hour express service is available for an extra $20.

Semester Examination Registration and Deadlines: Examination registration opens on the Student Portal 4 weeks prior to semester end-term examinations. Students must verify course codes and settle fee dues before registering. Registration deadlines are November 15 for the Fall semester and April 15 for the Spring semester. A late registration fee of $25 is charged for submissions within 5 days past the deadline.

Answer Script Revaluation and Inspection: Students dissatisfied with exam evaluations may apply for paper revaluation or obtain copies of their evaluated answer sheets within 10 calendar days of result publication. The fee is $10 per course for an answer sheet copy and $20 for full revaluation. If revaluation results in a grade change of 10% or greater, the revaluation fee is fully refunded.

Attendance Rules and 75 Percent Requirement: Greenfield Institute strictly mandates a minimum of 75% attendance in each enrolled theory and practical laboratory course. Students with attendance between 65% and 74% due to medical conditions or approved college representation may apply for attendance condonation with medical certificates and a $50 condonation fee. Attendance below 65% results in course detention (Grade FA).

Semester Tuition Fee Payment Deadlines and Fines: Semester tuition fees must be cleared online through the Greenfield Finance Portal (finance.greenfield.edu) within the first 10 calendar days of each semester. A late fine of $10 per day is applied for up to 14 days. If dues remain unpaid after 14 days, student portal access and course registration are suspended until settled at Accounts Office Room 105.

Student Leave Application and Medical Absence: For leave exceeding 2 consecutive days, students must submit a formal leave application. For medical illness, an authentic medical certificate signed by a physician must be submitted to the Faculty Advisor within 3 working days of returning. Duty leave for representing the college in sports or conferences requires prior written approval from the HOD.

Student ID Card Replacement Procedure: In case of lost or damaged student ID cards, report the loss immediately to Campus Security. Apply for a replacement card at Administrative Block Counter 3 or online using form GIT-ID-02 and pay a $15 replacement fee. The new smart RFID identity card is issued within 3 working days.

Course Add and Drop Procedure: Students may add or drop elective courses during the first two weeks (14 calendar days) of the semester via the Student Portal. Approval from the Faculty Advisor and Course Instructor is required. Courses dropped within this 2-week window do not appear on transcripts and carry no academic or financial penalty.

Degree Clearance and No Dues Process: Graduating students must complete the digital No Dues clearance process before collecting their degree certificates. Approvals must be obtained online from the Library, Department Labs, Hostels, Sports Office, and Accounts. Processing takes 7 business days following the release of final semester results.""",

    "campus_services.txt": """Training and Placement Cell (T&P): The Training and Placement Cell is located on the 2nd Floor of the Corporate Relations Block. Contact email is placement@greenfield.edu, phone extension is 4010. Over 150 top companies visit campus every year. Students become eligible for campus recruitment drives in the 6th semester provided they maintain a minimum CGPA of 6.5 with no standing backlogs.

Student Counselling and Mental Health Center (MindWell): The 'MindWell' Counselling Center offers free, confidential psychological counselling, stress management, and emotional support. Located in the Health and Wellness Wing, Room 108. Open Monday through Friday from 9:00 AM to 5:00 PM. Book appointments confidentially via mindwell@greenfield.edu or call the 24/7 crisis helpline at extension 4444.

Scholarships and Financial Aid Schemes: Greenfield Institute offers three primary scholarship categories: Merit Scholarships provide up to 50% tuition waiver for the top 5% of students in each branch; Need-Based Aid covers up to 75% tuition for students with family income under $15,000; and Sports Scholarships offer up to 40% fee waiver for national athletes. Applications open every August at portal.greenfield.edu/scholarships.

Campus Health Center and Emergency Medical Care: The Campus Health Center provides 24/7 outpatient medical care, first aid, emergency treatment, and free ambulance services. Located adjacent to Oak Hall. Staffed by 2 full-time physicians and nursing staff. Medical consultations and basic medications are completely free for all enrolled students. Emergency extension: 1111 or 1112.

Student Grievance Redressal Cell and Anti-Ragging: The Grievance Redressal Cell and Anti-Ragging Committee address student complaints regarding discrimination, grading discrepancies, or campus harassment with strict confidentiality. Complaints can be filed online at grievance.greenfield.edu or placed in physical complaint boxes outside the Admin Block. Committee head is Prof. Arthur Pendelton. Resolution is guaranteed within 15 working days.

Student Clubs and Extracurricular Activities: Greenfield Institute features over 25 active student clubs, including the ByteCraft Coding Club, Robotics Club, Thespians Drama Society, Acoustics Music Club, Literary & Debate Society, and Eco Club. Club recruitment takes place during the annual 'Club Carnival' in the 3rd week of September. Visit Student Activity Center (SAC) Room 101 or contact clubs@greenfield.edu.

Campus IT Helpdesk and Technical Support: The IT Helpdesk assists students with campus Wi-Fi configuration, university email access, portal password resets, and educational software licenses (Microsoft 365, MATLAB, AutoCAD). Located in Turing Block Ground Floor, Room 005. Hours are Monday to Saturday, 8:30 AM to 6:00 PM. Email: ithelpdesk@greenfield.edu, phone extension: 3199.

Campus Lost and Found Department: The Lost and Found office is operated by Campus Security Services at the Security Gate 1 Headquarters. Found items such as ID cards, electronics, books, and keys are logged into the online database at lostfound.greenfield.edu. Students can claim lost property Monday through Friday, 9:00 AM to 5:00 PM, by presenting valid student ID.

International Student Support Services: The International Students Office assists overseas students with visa extensions, FRRO registration, cultural orientation, and residential assistance. Located in the Gateway Building, Room G-12. Official email: international@greenfield.edu, phone extension: 1025. Office hours: Monday through Friday, 9:00 AM to 5:00 PM.

Women's Development Cell and Internal Complaints Committee (ICC): Greenfield Institute upholds a zero-tolerance policy against gender harassment. The ICC conducts workshops and reviews grievances with complete confidentiality. Presiding Officer is Dr. Marianne Cole. Office location is Newton Complex, Room 202. Direct 24/7 confidential helpline: extension 9999 or email icc@greenfield.edu."""
}

DATA_DIR = Path("data")
chunks: list[str] = []
chunk_embeddings: np.ndarray = np.array([])
embed_model: SentenceTransformer | None = None


def init_knowledge_base():
    global chunks, chunk_embeddings, embed_model

    # Auto-create data directory and write sample files if empty or non-existent
    if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for filename, content in SAMPLE_DATA.items():
            file_path = DATA_DIR / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")

    # Load all txt chunks from data directory
    loaded_chunks = []
    for file_path in sorted(DATA_DIR.glob("*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            raw_paragraphs = file_content.split("\n\n")
            for para in raw_paragraphs:
                cleaned = para.strip()
                if cleaned:
                    loaded_chunks.append(cleaned)

    chunks = loaded_chunks

    # Initialize SentenceTransformer model and compute normalized embeddings
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    if chunks:
        embeddings = embed_model.encode(chunks, normalize_embeddings=True)
        chunk_embeddings = np.array(embeddings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_knowledge_base()
    yield


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/")
def serve_index():
    return FileResponse("index.html")


@app.get("/style.css")
def serve_css():
    return FileResponse("style.css")


@app.get("/script.js")
def serve_js():
    return FileResponse("script.js")


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    question = req.question.strip()
    if not question:
        return ChatResponse(answer="Please enter a question.", sources=[])

    if embed_model is None or chunk_embeddings.size == 0 or len(chunks) == 0:
        return ChatResponse(
            answer="Knowledge base is not initialized. Please check the data folder.",
            sources=[]
        )

    # Compute normalized embedding for the query and retrieve top 3 chunks by cosine similarity
    query_emb = embed_model.encode([question], normalize_embeddings=True)[0]
    scores = np.dot(chunk_embeddings, query_emb)
    k = min(3, len(chunks))
    top_indices = np.argsort(scores)[::-1][:k]
    top_chunks = [chunks[i] for i in top_indices]

    # Verify Groq API key configuration
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or not groq_api_key.strip():
        return ChatResponse(
            answer="Groq API key is missing. Please add GROQ_API_KEY to your .env file and restart the server.",
            sources=top_chunks
        )

    # Generate answer using Groq API
    try:
        from groq import Groq

        context = "\n\n---\n\n".join(top_chunks)
        prompt = (
            "Answer ONLY using the context below. If the answer isn't in the context, "
            "say you don't know and suggest contacting the college office. Be short and clear.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )

        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        answer = completion.choices[0].message.content.strip()
        return ChatResponse(answer=answer, sources=top_chunks)

    except Exception as e:
        return ChatResponse(
            answer=f"An error occurred while connecting to Groq: {str(e)}",
            sources=top_chunks
        )
