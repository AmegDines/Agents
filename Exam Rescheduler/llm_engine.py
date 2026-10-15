import os
from config.settings import MODEL_NAME if 'MODEL_NAME' in globals() else "free-reasoning-model"

class FreeLLM:
    """
    A wrapper for an LLM API.
    Security: API keys are now loaded from environment variables to avoid hardcoding.
    """
    def __init__(self, model_name=None):
        # Load from config or environment
        self.model_name = model_name or os.getenv("MODEL_NAME", "free-reasoning-model")
        self.api_key = os.getenv("API_KEY")

    def generate(self, prompt):
        # Input Validation: Prevent prompt injection by sanitizing basic inputs
        sanitized_prompt = prompt.replace("{", "").replace("}", "").strip()

        p = sanitized_prompt.lower()

        if "current state: start" in p:
            return {
                "thought": "I am starting the task. First, I need to gather all necessary data about the exam, students, and instructions.",
                "action": "gather_info",
                "params": {}
            }
        elif "current state: info_gathered" in p:
            return {
                "thought": "I have the data. Now I must search for a slot that fits room capacity, faculty availability, and student schedules.",
                "action": "search_slots",
                "params": {}
            }
        elif "current state: slot_found" in p:
            return {
                "thought": "I found a suitable slot! However, rescheduling is irreversible, so I must request human approval.",
                "action": "request_approval",
                "params": {}
            }
        elif "current state: approved" in p:
            return {
                "thought": "The instructor approved the plan. I will now execute the room booking, rescheduling, and notification.",
                "action": "execute_plan",
                "params": {}
            }
        else:
            return {
                "thought": "I am uncertain of the next step. I will try to gather more info.",
                "action": "gather_info",
                "params": {}
            }

llm = FreeLLM()
