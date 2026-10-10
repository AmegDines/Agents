import json
from datetime import datetime

class DecisionTrace:
    def __init__(self):
        self.trace = []

    def log(self, action, result, reasoning):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "reasoning": reasoning
        }
        self.trace.append(entry)
        print(f"[TRACE] {action} -> {reasoning}")

    def save(self, filename="decision_trace.json"):
        with open(filename, "w") as f:
            json.dump(self.trace, f, indent=2)
        print(f"Decision trace saved to {filename}")

    def get_report(self):
        report = "# Decision Trace Report\n\n"
        for i, entry in enumerate(self.trace):
            report += f"## Step {i+1}: {entry['action']}\n"
            report += f"- **Reasoning**: {entry['reasoning']}\n"
            report += f"- **Result**: {json.dumps(entry['result'], indent=2)}\n\n"
        return report

trace_logger = DecisionTrace()
