<div align="center">
  <img src="https://raw.githubusercontent.com/T-dot-ux/IBM-SkillsBuild-VerifyAI/main/frontend/public/mascot_safe.png" alt="VerifyAI Logo" width="150"/>
  <h1>VerifyAI – Your Digital Trust Copilot</h1>
  <p><strong>AI-powered document and web verification. Instantly detect scams, verify sources, and proceed with confidence.</strong></p>
</div>

---

### 🏆 Project Details

- **Internship:** AICTE | IBM SkillsBuild AI Automation & Intelligent Solutions Internship | BharatCares 2026
- **Team Name:** MATRIX PLEX
- **Team ID:** IBMBH06603
- **Institution:** Vivekananda Institute of Professional Studies – Technical Campus, Delhi
- **Team Size:** 6 Members

---

## 👥 Meet the Team

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

## 📖 Walkthrough & Architecture

VerifyAI is an advanced Agentic AI system that validates digital content (URLs, documents, text) using a coordinated swarm of specialized AI agents.

### The Pipeline
1. **Input Agent:** Ingests the data and extracts key entities.
2. **Threat Detection Agent:** Analyzes the data for phishing indicators, malware patterns, and spoofing.
3. **Source Credibility Agent:** Cross-references the domain or source against known reputation databases.
4. **Evidence Verification Agent:** fact-checks the extracted entities.
5. **Validation & Consensus Engine:** A central governance layer that intercepts contradictory agent reports and resolves them using an LLM consensus heuristic.
6. **Decision Engine:** Computes a deterministic Trust Score and Verdict.
7. **Report Agent:** Synthesizes the findings into a human-readable, evidence-based executive summary.

---

## 📂 Project Structure

```text
IBM_VerifyAI/
├── backend/
│   ├── agents/          # Specialized AI Agents (Master, Threat, Source, Consensus, etc.)
│   ├── api/             # FastAPI routers (chat, verify, history)
│   ├── core/            # Governance engines, security, and structured loggers
│   ├── models/          # SQLite Database models
│   ├── schemas/         # Pydantic data contracts (AgentMessages, Indicators)
│   ├── tests/           # Regression tests for deterministic outcomes
│   └── main.py          # FastAPI application entry point
│
├── frontend/
│   ├── public/          # Static assets and mascot images
│   ├── src/
│   │   ├── app/         # Next.js App Router (Landing, Dashboard, History)
│   │   ├── components/  # React components (Animations, Auth, Layouts)
│   │   └── lib/         # API configurations
│   ├── package.json     # Node.js dependencies
│   └── tailwind.config.ts # Tailwind styling config
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Google Gemini API Key

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:** Create a `.env` file in the `backend/` directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=a_secure_random_string
   ```
5. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The backend will be available at `http://localhost:8000`.*

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Run the Next.js development server:**
   ```bash
   npm run dev
   ```
   *The frontend will be available at `http://localhost:3000`.*

---

## 💻 Usage

1. Open your browser and navigate to `http://localhost:3000`.
2. Click **ENTER SYSTEM** to access the dashboard.
3. Upload a document or submit a URL for verification.
4. Watch the agents work in parallel via the real-time UI.
5. Review the final Trust Score, Risk Indicators, and Evidence-based Summary.
