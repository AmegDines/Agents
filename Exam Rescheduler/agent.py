from erp_mock import erp
from trace_logger import trace_logger
from llm_engine import llm

class ExamReschedulerAgent:
    def __init__(self, exam_id):
        self.exam_id = exam_id
        self.state = "START"
        self.context = {}
        self.budget = 40
        self.call_count = 0

    def _call_tool(self, tool_name, *args, **kwargs):
        """Internal helper to handle tool calls, budget, and logging."""
        self.call_count += 1
        if self.call_count > self.budget:
            raise Exception("Tool call budget exceeded!")

        # Resolve the tool from the Mock ERP
        tool_func = getattr(erp, tool_name)
        result = tool_func(*args, **kwargs)

        # Log the action
        trace_logger.log(tool_name, result, f"Agent called {tool_name} to progress towards the goal.")
        return result

    def run(self):
        print(f"--- Agent starting task for {self.exam_id} ---")

        while self.state != "COMPLETED":
            # 1. REASONING (The Brain)
            prompt = f"Current state: {self.state}. Exam ID: {self.exam_id}. Context: {self.context}. Decide the next action."
            decision = llm.generate(prompt)

            thought = decision.get("thought", "No thought provided.")
            action = decision.get("action")
            params = decision.get("params", {})

            print(f"\n[THOUGHT] {thought}")
            print(f"[ACTION] {action}")

            # 2. ACTING (The Hands)
            try:
                if action == "gather_info":
                    exam_details = self._call_tool("get_exam", self.exam_id)
                    students = self._call_tool("get_enrolled_students", self.exam_id)
                    inbox = self._call_tool("read_inbox")
                    self.context.update({
                        "exam": exam_details,
                        "students": students,
                        "inbox": inbox
                    })
                    self.state = "INFO_GATHERED"

                elif action == "search_slots":
                    # The agent's internal logic for calculating the slot
                    # This part is often a 'skill' or a specialized tool call.
                    exam = self.context.get("exam")
                    students = self.context.get("students")

                    if not exam or not students:
                        self.state = "START" # Reset if info missing
                        continue

                    required_capacity = len(students) * 2 - 1
                    invigilators = exam["faculty"]

                    # Simplified search for the agent
                    possible_dates = ["2026-10-13", "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-17"]
                    possible_slots = ["10:00 AM", "02:00 PM"]
                    found_slot = None

                    for date in possible_dates:
                        for slot in possible_slots:
                            rooms = self._call_tool("list_rooms", date, slot)
                            suitable_rooms = [r for r in rooms if r["capacity"] >= required_capacity]
                            if not suitable_rooms: continue

                            all_faculty_avail = True
                            for faculty_id in invigilators:
                                avail = self._call_tool("get_faculty_availability", faculty_id, date)
                                if not avail.get(slot, False):
                                    all_faculty_avail = False
                                    break
                            if not all_faculty_avail: continue

                            schedules = self._call_tool("get_student_schedule", students)
                            has_clash = False
                            for sid in students:
                                student_day = schedules.get(sid, {})
                                if slot in student_day.get(date, []):
                                    has_clash = True
                                    break
                            if has_clash: continue

                            found_slot = {"date": date, "slot": slot, "room": suitable_rooms[0]["room"], "invigilators": invigilators}
                            break
                        if found_slot: break

                    if found_slot:
                        self.context["found_slot"] = found_slot
                        self.state = "SLOT_FOUND"
                    else:
                        self.state = "NO_SLOT_FOUND"

                elif action == "request_approval":
                    slot = self.context.get("found_slot")
                    if not slot:
                        self.state = "INFO_GATHERED"
                        continue

                    summary = f"Proposed Reschedule: {slot['date']} at {slot['slot']} in room {slot['room']}."
                    approved = self._call_tool("request_human_approval", summary)
                    if approved:
                        self.state = "APPROVED"
                    else:
                        self.state = "DENIED"

                elif action == "execute_plan":
                    slot = self.context.get("found_slot")
                    students = self.context.get("students")
                    exam = self.context.get("exam")

                    if not slot or self.state != "APPROVED":
                        self.state = "INFO_GATHERED"
                        continue

                    self._call_tool("book_room", slot['room'], slot['date'], slot['slot'])
                    self._call_tool("reschedule_exam", self.exam_id, slot['date'], slot['slot'], [slot['room']])
                    self._call_tool("send_notice", students + exam["faculty"], "Exam Rescheduled!")

                    self.state = "COMPLETED"

                else:
                    print(f"Unknown action: {action}")
                    self.state = "START"

            except Exception as e:
                print(f"Error during action: {e}")
                self.state = "START"

        print("\n--- Agent task completed successfully! ---")
        trace_logger.save()

if __name__ == "__main__":
    agent = ExamReschedulerAgent("CSE476")
    agent.run()
