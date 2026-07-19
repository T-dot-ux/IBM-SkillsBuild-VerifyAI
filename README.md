<div align="center">
  <img src="https://raw.githubusercontent.com/T-dot-ux/IBM-SkillsBuild-VerifyAI/main/frontend/public/mascot_safe.png" alt="VerifyAI Logo" width="150"/>
  <h1>VerifyAI – Your Digital Trust Copilot</h1>
  <p><strong>AI-powered document and web verification. Instantly detect scams, verify sources, and proceed with confidence.</strong></p>
</div>

---

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture & Agent Workflow](#-architecture--agent-workflow)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [1. Repository Clone](#1-repository-clone)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Running the Full Project](#-running-the-full-project)
- [Folder Structure](#-folder-structure)
- [API Endpoints](#-api-endpoints)
- [Example Requests/Responses](#-example-requestsresponses)
- [Troubleshooting](#-troubleshooting)
- [Future Roadmap](#-future-roadmap)
- [Meet the Team](#-meet-the-team)
- [Acknowledgements](#-acknowledgements)
- [License](#-license)

---

## 🌟 Project Overview

**VerifyAI** is a robust, production-grade agentic AI system designed to validate digital content—including URLs, documents, and text—using a swarm of specialized AI agents. Built as the capstone project for the **AICTE | IBM SkillsBuild AI Automation & Intelligent Solutions Internship (BharatCares 2026)**, it serves as a "Digital Trust Copilot" to protect users from phishing, scams, and misinformation.

---

## ✨ Features

- **Multi-Modal Input:** Upload documents (PDFs/Images), paste URLs, or type raw text.
- **Swarm Intelligence:** specialized AI agents (Threat Detection, Source Credibility, Evidence Verification) analyze the input in parallel.
- **Deterministic Governance:** A strict Validation and Consensus Engine resolves agent conflicts to provide a highly accurate, explainable Trust Score.
- **Evidence-Based Summaries:** Dynamic reporting powered by Google Gemini, generating clear explanations of the verdict without hallucinated placeholders.
- **Real-Time Interactive UI:** A stunning Next.js dashboard featuring Framer Motion animations and live status updates.
- **Multilingual Support:** Interact via text or voice in English and Hindi.

---

## 🛠 Tech Stack

**Frontend:**
- [Next.js 14](https://nextjs.org/) (React Framework)
- [Tailwind CSS](https://tailwindcss.com/) (Styling)
- [Framer Motion](https://www.framer.com/motion/) (Animations)
- [Lucide React](https://lucide.dev/) (Icons)

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python web framework)
- [Google Gemini API](https://ai.google.dev/) (Core LLM capabilities)
- [Pydantic](https://docs.pydantic.dev/) (Data validation and schemas)
- [SQLite](https://www.sqlite.org/) (Lightweight local database)

---

## 🧠 Architecture & Agent Workflow

VerifyAI relies on an orchestrated multi-agent pipeline:

1. **Input Agent:** Ingests the raw data, identifies the modality (URL vs Document), and extracts entities.
2. **Threat Detection Agent:** Analyzes the data for phishing indicators, urgency tactics, and malware patterns.
3. **Source Credibility Agent:** Cross-references domains and sources against reputation logic.
4. **Evidence Verification Agent:** Fact-checks extracted entities and verifies claims.
5. **Validation Engine:** Intercepts the reports. If one agent claims a critical threat while another claims safety, it halts and flags a conflict.
6. **Consensus Agent:** Uses LLM heuristics to resolve conflicts flagged by the Validation Engine.
7. **Decision Engine:** Computes a final, deterministic Trust Score (0-100), Risk Level, and Verdict.
8. **Report Agent:** Synthesizes the final evidence into a human-readable executive summary.

![Architecture Flow Placeholder](https://raw.githubusercontent.com/T-dot-ux/IBM-SkillsBuild-VerifyAI/main/frontend/public/mascot_safe_tight.png)

---

## ⚙️ Prerequisites

Before you begin, ensure you have met the following requirements:
- **Node.js** (v18.0.0 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.10 or higher) - [Download here](https://www.python.org/)
- **Git** - [Download here](https://git-scm.com/)
- A valid **Google Gemini API Key** - [Get one here](https://aistudio.google.com/)

---

## 🚀 Installation & Setup

### 1. Repository Clone

First, clone the repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/T-dot-ux/IBM-SkillsBuild-VerifyAI.git
cd IBM-SkillsBuild-VerifyAI
```

### 2. Backend Setup

Open a new terminal window to set up the FastAPI backend.

**Navigate to the backend directory:**
```bash
cd backend
```

**Virtual Environment Setup:**
Create a secure, isolated Python environment.
```bash
python -m venv venv
```

**Activate the Virtual Environment:**
- **On Windows:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

**Dependency Installation:**
Install the required Python packages.
```bash
pip install -r requirements.txt
```

**Environment Variables (.env):**
Create a `.env` file in the root of the `backend` directory. 
```bash
# On Mac/Linux
touch .env

# On Windows
New-Item -Path .env -ItemType File
```
Open the `.env` file in your code editor and add the following:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=a_secure_random_string_for_jwt
```

**Database Setup:**
The backend utilizes SQLite. The database file (`verifyai.db`) will automatically initialize when you start the server or run a verification for the first time. No manual migrations are required.

**Running Backend:**
Start the FastAPI server with hot-reloading:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*The backend API will now be running at `http://localhost:8000`.*

### 3. Frontend Setup

Open a **second terminal window** (keep the backend running in the first).

**Navigate to the frontend directory:**
```bash
cd frontend
```

**Dependency Installation:**
Install the required Node packages.
```bash
npm install
```

**Running Frontend:**
Start the Next.js development server:
```bash
npm run dev
```
*The frontend web app will now be running at `http://localhost:3000`.*

---

## 🏃 Running the Full Project

To successfully use the app locally:
1. Ensure the **Backend** is running (`uvicorn main:app --reload` on port 8000).
2. Ensure the **Frontend** is running (`npm run dev` on port 3000).
3. Open your browser and navigate to `http://localhost:3000`.
4. Click **"ENTER SYSTEM"** to access the dashboard and upload a file or URL.

---

## 📁 Folder Structure

```text
IBM-SkillsBuild-VerifyAI/
├── backend/
│   ├── agents/          # Agentic AI logic (Master, Threat, Source, Consensus, Report)
│   ├── api/             # FastAPI routers (chat, verify, history, auth)
│   ├── core/            # Governance, Security, and Structured Logging
│   ├── models/          # SQLite database models
│   ├── schemas/         # Pydantic data contracts (AgentMessages, Indicators)
│   ├── tests/           # Regression tests
│   ├── main.py          # FastAPI entry point
│   └── requirements.txt # Python dependencies
│
├── frontend/
│   ├── public/          # Static assets (Mascots, SVGs)
│   ├── src/
│   │   ├── app/         # Next.js App Router (Landing, Dashboard)
│   │   ├── components/  # React components (Animations, Auth, Layouts, Verify)
│   │   └── lib/         # API configurations and utility functions
│   ├── package.json     # Node dependencies
│   └── tailwind.config.ts
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🌐 API Endpoints

The backend provides several core REST endpoints. You can view the interactive Swagger UI by visiting `http://localhost:8000/docs`.

- `POST /api/verify`: Submits a text string or URL for verification.
- `POST /api/verify/document`: Submits a file (PDF/Image) for verification.
- `GET /api/history`: Retrieves past verification history.
- `POST /api/chat`: Interacts with the contextual AI chat assistant.

---

## 📝 Example Requests/Responses

**Verify a URL (cURL Request):**
```bash
curl -X POST "http://localhost:8000/api/verify" \
     -H "Content-Type: application/json" \
     -d '{"content": "http://suspicious-freemoney.com", "content_type": "url"}'
```

**JSON Response (Abridged):**
```json
{
  "job_id": "84d24a91-4e78-43db",
  "trust_score": 15,
  "confidence_score": 90,
  "verdict": {
    "level": "CRITICAL",
    "color": "bg-red-500",
    "message": "Do Not Proceed"
  },
  "summary": "This URL exhibits critical phishing indicators, including an urgency tactic and a recently registered domain name designed to mimic a financial institution.",
  "evidence": [
    {
      "source": "ThreatDetectionAgent",
      "severity": "CRITICAL",
      "finding": "Domain name closely mimics a known banking portal."
    }
  ]
}
```

---

## 🛠 Troubleshooting

**1. Port 8000 is already in use:**
If another application is using port 8000, you can run FastAPI on a different port:
```bash
uvicorn main:app --reload --port 8001
```
*(Remember to update `NEXT_PUBLIC_API_URL` in your frontend `.env.local` if you do this).*

**2. Gemini API Errors:**
Ensure your `GEMINI_API_KEY` is correct in `backend/.env`. If you receive a 401 Unauthorized or 429 Too Many Requests error, verify your quota limits on Google AI Studio.

**3. "Module Not Found" in Python:**
Ensure your virtual environment is activated before running `pip install` or `uvicorn`. Your terminal prompt should usually show `(venv)` at the beginning.

---

## 📸 Screenshots

![Dashboard Screenshot Placeholder](https://raw.githubusercontent.com/T-dot-ux/IBM-SkillsBuild-VerifyAI/main/frontend/public/mascot_danger.png)

---

## 🚀 Future Roadmap

- [ ] **Real-Time Phishing Database Integration:** Integrate with Google Safe Browsing API.
- [ ] **Browser Extension:** Create a Chrome extension to verify sites in real-time.
- [ ] **Learning Agent Implementation:** Allow the system to learn from manual user feedback and overrides.

---

## 👥 Meet the Team

**MATRIX PLEX (Team ID: IBMBH06603)**

<table align="center">
  <tr>
    <td align="center"><a href="https://github.com/T-dot-ux"><img src="https://github.com/T-dot-ux.png" width="100px;" alt="Tanish Rajput"/><br /><sub><b>Tanish Rajput</b></sub><br /><sub><i>Team Leader</i></sub></a></td>
    <td align="center"><a href="https://github.com/devansh3912"><img src="https://github.com/devansh3912.png" width="100px;" alt="Devansh"/><br /><sub><b>Devansh</b></sub><br /><sub><i>Team Member</i></sub></a></td>
    <td align="center"><a href="https://github.com/Dhruv7946"><img src="https://github.com/Dhruv7946.png" width="100px;" alt="Dhruv"/><br /><sub><b>Dhruv</b></sub><br /><sub><i>Team Member</i></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/Kunal9213"><img src="https://github.com/Kunal9213.png" width="100px;" alt="Kunal"/><br /><sub><b>Kunal</b></sub><br /><sub><i>Team Member</i></sub></a></td>
    <td align="center"><a href="https://github.com/SaKsHaMkAkAr15"><img src="https://github.com/SaKsHaMkAkAr15.png" width="100px;" alt="Saksham Kakar"/><br /><sub><b>Saksham Kakar</b></sub><br /><sub><i>Team Member</i></sub></a></td>
    <td align="center"><a href="https://github.com/yougantersingh1168-glitch"><img src="https://github.com/yougantersingh1168-glitch.png" width="100px;" alt="Youganter Singh"/><br /><sub><b>Youganter Singh</b></sub><br /><sub><i>Team Member</i></sub></a></td>
  </tr>
</table>

---

## 🙏 Acknowledgements

- **IBM SkillsBuild & AICTE** for the incredible internship opportunity.
- **BharatCares** for hosting and facilitating the program.
- **Google DeepMind** for providing the Gemini API used heavily in our architecture.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
