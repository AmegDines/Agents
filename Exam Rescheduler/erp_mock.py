import json
import logging
from datetime import datetime, timedelta

# --- Mock ERP Database ---
# This simulates the university's backend data.
ERP_DATA = {
    "exams": {
        "CSE476": {
            "name": "CSE476 End-Term",
            "students": ["S1", "S2", "S3", "S4", "S5"], # Small set for testing, 180 for real
            "faculty": ["F1", "F2"],
            "date": "2026-10-16", # Friday
            "slot": "10:00 AM",
            "rooms": ["R101"]
        }
    },
    "rooms": {
        "R101": {"capacity": 200},
        "R102": {"capacity": 400},
        "R103": {"capacity": 100},
    },
    "room_bookings": {
        # (room, date, slot) -> exam_id
        ("R101", "2026-10-16", "10:00 AM"): "CSE476",
        ("R102", "2026-10-17", "10:00 AM"): "OTHER1",
    },
    "faculty_availability": {
        # (faculty_id, date) -> {slot: available}
        "F1": {
            "2026-10-16": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-17": {"10:00 AM": True, "02:00 PM": False},
            "2026-10-18": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-19": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-20": {"10:00 AM": True, "02:00 PM": True},
        },
        "F2": {
            "2026-10-16": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-17": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-18": {"10:00 AM": False, "02:00 PM": True},
            "2026-10-19": {"10:00 AM": True, "02:00 PM": True},
            "2026-10-20": {"10:00 AM": True, "02:00 PM": True},
        },
    },
    "student_schedules": {
        # student_id -> {date: [slots]}
        "S1": {"2026-10-17": ["10:00 AM"]},
        "S2": {"2026-10-18": ["02:00 PM"]},
        "S3": {},
        "S4": {"2026-10-19": ["10:00 AM"]},
        "S5": {},
    },
    "inbox": [
        {"from": "Dean", "message": "Please ensure the CSE476 exam is rescheduled away from the University Gala on Friday morning."}
    ]
}

class MockERP:
    def __init__(self):
        self.call_count = 0

    def _increment(self):
        self.call_count += 1

    def get_exam(self, exam_id):
        self._increment()
        return ERP_DATA["exams"].get(exam_id)

    def list_rooms(self, date, slot):
        self._increment()
        available = []
        for room in ERP_DATA["rooms"]:
            if (room, date, slot) not in ERP_DATA["room_bookings"]:
                available.append({"room": room, "capacity": ERP_DATA["rooms"][room]["capacity"]})
        return available

    def get_room_bookings(self, room, date):
        self._increment()
        bookings = []
        for (r, d, s), exam in ERP_DATA["room_bookings"].items():
            if r == room and d == date:
                bookings.append({"slot": s, "exam": exam})
        return bookings

    def get_faculty_availability(self, faculty_id, date):
        self._increment()
        day_avail = ERP_DATA["faculty_availability"].get(faculty_id, {}).get(date, {})
        return day_avail

    def get_enrolled_students(self, course):
        self._increment()
        exam = ERP_DATA["exams"].get(course)
        return exam["students"] if exam else []

    def get_student_schedule(self, student_ids):
        self._increment()
        schedules = {}
        for sid in student_ids:
            schedules[sid] = ERP_DATA["student_schedules"].get(sid, {})
        return schedules

    def read_inbox(self):
        self._increment()
        return ERP_DATA["inbox"]

    def book_room(self, room, date, slot):
        self._increment()
        ERP_DATA["room_bookings"][(room, date, slot)] = "PENDING"
        return True

    def reschedule_exam(self, exam_id, date, slot, rooms):
        self._increment()
        exam = ERP_DATA["exams"].get(exam_id)
        if not exam: return False

        # Remove old booking
        old_date = exam["date"]
        old_slot = exam["slot"]
        old_room = exam["rooms"][0] # Simplified
        ERP_DATA["room_bookings"].pop((old_room, old_date, old_slot), None)

        # Update exam
        exam["date"] = date
        exam["slot"] = slot
        exam["rooms"] = rooms

        # Add new bookings
        for r in rooms:
            ERP_DATA["room_bookings"][(r, date, slot)] = exam_id
        return True

    def send_notice(self, recipients, message):
        self._increment()
        print(f"NOTIFYING {recipients}: {message}")
        return True

    def request_human_approval(self, summary):
        self._increment()
        print(f"\n--- APPROVAL REQUEST ---\n{summary}\n------------------------")
        # In a real scenario, this would wait for input.
        # For the mock, we'll simulate approval.
        return True

erp = MockERP()
