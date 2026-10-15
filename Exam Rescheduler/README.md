# Exam Rescheduler Agent
An autonomous AI agent that reschedules university exams while strictly adhering to room capacity, faculty availability, and student schedules.

## 🚀 Features
- **LLM-Driven Reasoning**: Uses a reasoning loop to decide actions.
- **Constraint Satisfaction**: Validates slots against multiple criteria.
- **Human-in-the-Loop**: Requires explicit approval for irreversible actions.
- **Audit Trail**: Generates a full decision trace for every run.

## 🛠️ Installation
```bash
git clone https://github.com/yourusername/exam-rescheduler.git
cd exam-rescheduler
pip install -r requirements.txt
```

## 📖 Usage
Run the agent directly:
```bash
python agent.py
```
Or explore the demonstration:
```bash
jupyter notebook exam_rescheduler_demo.ipynb
```

## 🔒 Security
- API keys are managed via `.secrets/env.txt` (excluded from git).
- Input sanitization is implemented in the LLM engine to prevent prompt injection.
- Tool call budget is strictly enforced to prevent infinite loops.
