import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("Missing GROQ_API_KEY. Set it first.")

client = Groq(api_key=api_key)

class InterviewAgent:
    def __init__(self, role_requirements):
        self.role_requirements = role_requirements
        self.transcript = []

    def analyze_resume(self, resume_text):
        weak_points = [req for req in self.role_requirements if req.lower() not in resume_text.lower()]
        return weak_points[:3]

    def ask_question(self, weak_point):
        prompt = f"Generate a probing interview question for weak point: {weak_point}"
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    def evaluate_answer(self, answer):
        return len(answer.split()) < 15

    def conduct_interview(self, resume_text, candidate_answers):
        weak_points = self.analyze_resume(resume_text)
        for wp, ans in zip(weak_points, candidate_answers):
            q = self.ask_question(wp)
            self.transcript.append({"question": q, "answer": ans})
            if self.evaluate_answer(ans):
                followup = self.ask_question(f"dig deeper on {wp}")
                self.transcript.append({"question": followup, "answer": "candidate follow-up answer"})
        return self.transcript

class EvaluatorAgent:
    def evaluate(self, transcript):
        prompt = f"Transcript: {transcript}\nVerdict Ready/Not Ready with reasoning."
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

role_reqs = ["Python", "SQL", "APIs", "Concurrency"]
resume_text = "Experienced in Java, some SQL..."
candidate_answers = ["I used SQL lightly", "I built APIs", "Concurrency not much"]

agent1 = InterviewAgent(role_reqs)
transcript = agent1.conduct_interview(resume_text, candidate_answers)

agent2 = EvaluatorAgent()
verdict = agent2.evaluate(transcript)

print("Transcript:", transcript)
print("Verdict:", verdict)