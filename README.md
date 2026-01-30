# AI-Powered Applicant Tracking System (ATS)

An end-to-end **AI-powered Applicant Tracking System** that helps recruiters post jobs, evaluate candidates, and make data-driven hiring decisions using automated resume–job matching.

---

## 🚀 Features

### 👨‍💼 Recruiter
- Create and manage job postings
- View all applicants per job
- See AI-generated **match scores**
- Identify **missing skills** per candidate
- Update application status: **Shortlist / Interview / Reject**
- View **AI Insights** (top match, average match, skill gaps)

### 👩‍💻 Candidate
- Upload / update resume
- Browse available jobs
- Apply to jobs
- View application status in real time
- See match percentage and missing skills

---

## 🧠 AI Matching Logic
- Extracts skills from resumes and job descriptions
- Computes match score (%)
- Highlights missing required skills
- Ranks candidates per job automatically

---

## 🛠 Tech Stack

**Backend**
- Python
- FastAPI
- SQLite
- Pydantic

**Frontend**
- HTML
- CSS
- Vanilla JavaScript

---

## 📂 Project Structure
backend/
├── main.py
├── requirements.txt
├── core/
├── database/
├── routers/
├── services/
└── utils/

frontend/
├── index.html
├── dashboard.html
├── app.js
└── styles.css

---


## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

git clone https://github.com/DaggubatiBapaiah/AI-Powered-Applicant-Tracking-System-ATS.git
cd AI-Powered-Applicant-Tracking-System-ATS

2️⃣ Backend setup
cd backend
pip install -r requirements.txt
python main.py


Backend will run on:

http://localhost:5000

3️⃣ Frontend

Open frontend/index.html in your browser
(or serve it via any static server)

🧪 Demo Flow

https://github.com/user-attachments/assets/d5f4f2b1-790d-4a6d-b38b-41c8cf6485f7



Login as Recruiter → Post a job

Login as Candidate → Upload resume → Apply

Recruiter reviews applicants → views match score → updates status

Candidate sees real-time application updates

🔒 License

This project is licensed under the MIT License.

📌 Status

✅ Core features complete
🚧 Future improvements: authentication, resume PDF parsing, deployment

🙌 Author
Daggubati Bapaiah chowdary
