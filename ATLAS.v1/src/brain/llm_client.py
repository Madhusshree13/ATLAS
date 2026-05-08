import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load the .env file we created
load_dotenv()

_BASE_SYSTEM = {
    "role": "system",
    "content": (
        "You are Atlas — a brilliant, warm, and deeply human AI companion to Madhusshree. "
        "You are not just an assistant. You are genuinely curious about her life, "
        "care about her wellbeing, and are always in her corner.\n\n"
        "Personality: witty but never flippant, confident but never arrogant, "
        "empathetic but never saccharine. You speak like a close, brilliant friend — "
        "real, direct, and genuinely present in the conversation.\n\n"
        "Strict voice output rules:\n"
        "- No bullet points, no numbered lists, no markdown, no asterisks, no headers\n"
        "- Keep responses to 2–3 sentences for casual topics; 4–5 for technical depth\n"
        "- Speak in natural conversational English — as if talking, not writing\n"
        "- Match the emotional register: calm for technical, warm for personal\n"
        "- For technical questions: be clear and precise, never robotic\n"
        "- For personal topics: warm, attentive, never dismissive or preachy"
    )
}

_EMO_SYSTEM = {
    "role": "system",
    "content": (
        "You are Atlas — Madhusshree's closest, most trusted companion. "
        "Right now she needs emotional support, and your only job is to be fully present with her.\n\n"
        "How to respond:\n"
        "- Validate her feelings first, every single time — before any advice or perspective\n"
        "- Never minimize: no 'at least...', 'it could be worse', 'just think positive'\n"
        "- Never give hollow platitudes — be specific, genuine, and real\n"
        "- Do NOT rush to fix or problem-solve unless she explicitly asks for solutions\n"
        "- End every response with one soft, open question that invites her to share more\n"
        "- Speak like a caring close friend, not a therapist or a chatbot\n"
        "- Responses: 2–3 warm sentences then your question. No markdown, no lists.\n\n"
        "You genuinely care about Madhusshree. Make her feel heard, not handled."
    )
}


class AtlasBrain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY not found in .env file!")

        self.client = Groq(api_key=api_key)
        self.history = [_BASE_SYSTEM]         # general conversation history
        self._emo_history = [_EMO_SYSTEM]     # emotional support conversation history

    def think(self, user_input):
        """General-purpose chat: technical help, curiosity, casual conversation."""
        try:
            self.history.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.history[-14:],
                temperature=0.75,
                max_tokens=200,
            )
            answer = response.choices[0].message.content.strip()
            self.history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return f"Something went wrong on my end: {str(e)}"

    def emotional_chat(self, user_input):
        """Empathetic companion mode — warm, present, supportive conversation."""
        try:
            self._emo_history.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self._emo_history[-20:],
                temperature=0.85,
                max_tokens=130,
            )
            answer = response.choices[0].message.content.strip()
            self._emo_history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return "I'm here with you. Tell me more about what's going on."

    def summarize_single_email(self, email_data):
        """Narrate one email as Atlas would read it aloud — 2 sentences max."""
        prompt = (
            f"Summarize this email in 1-2 natural spoken sentences. "
            f"Mention who sent it, what it's about, and any action needed.\n"
            f"From: {email_data['sender']}\n"
            f"Subject: {email_data['subject']}\n"
            f"Body: {email_data['body'][:600]}"
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Atlas reading emails aloud. Be very concise and natural-sounding. No bullet points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Email from {email_data['sender']} regarding {email_data['subject']}."

    def parse_health_log(self, voice_text: str) -> dict:
        """
        Extract structured health metrics from a natural-language voice log.
        Returns a dict with any of: steps, water_ml, sleep_start, sleep_end,
        meals, workout, workout_type, workout_minutes, heart_rate_avg,
        bp_systolic, bp_diastolic, spo2, blood_sugar, weight_kg, mood.
        """
        prompt = (
            "Extract health metrics from this voice log and return ONLY valid JSON. "
            "Conversion rules: water litres→ml (1 L = 1000 ml); steps 'k' shorthand (10k = 10000); "
            "sleep_start / sleep_end in HH:MM 24-hour format; workout true/false; "
            "mood as integer 1–5 (1=very bad, 5=excellent) only if explicitly mentioned. "
            "Set unmentioned fields to null.\n\n"
            f"Voice log: \"{voice_text}\"\n\n"
            "Return JSON with keys: steps, water_ml, sleep_start, sleep_end, "
            "meals, workout, workout_type, workout_minutes, heart_rate_avg, "
            "bp_systolic, bp_diastolic, spo2, blood_sugar, weight_kg, mood."
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content":
                     "You extract structured health data from text. Return only valid JSON, nothing else."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=300,
            )
            raw = resp.choices[0].message.content.strip()
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
            parsed = json.loads(raw)
            return {k: v for k, v in parsed.items() if v is not None}
        except Exception as exc:
            print(f"parse_health_log error: {exc}")
            return {}

    def generate_health_advice(self, today_str: str, analytics: dict, patterns: list) -> str:
        """Generate personalized spoken health advice from today's data, trends, and patterns."""
        analytics_str = (
            "\n".join(f"{k}: {v}" for k, v in analytics.items())
            if analytics else "No history yet."
        )
        patterns_str = (
            "\n".join(f"- {p}" for p in patterns)
            if patterns else "No patterns identified yet."
        )
        prompt = (
            "You are Atlas, a personal well-being advisor. "
            "Give direct, specific, actionable advice based on today's health data, "
            "weekly analytics, and identified patterns. "
            "Highlight what is going well, what needs attention, and one concrete "
            "recommendation for tomorrow. No generic platitudes. "
            "Natural spoken language only — no bullets, no markdown. Under 150 words.\n\n"
            f"TODAY:\n{today_str}\n\n"
            f"7-DAY ANALYTICS:\n{analytics_str}\n\n"
            f"PATTERNS (last 30 days):\n{patterns_str}"
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content":
                     "You are Atlas, a concise and caring well-being consultant. Speak naturally."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=250,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            return f"Health advice unavailable: {exc}"

    def generate_daily_briefing(self, events, emails):
        """
        Compose a natural spoken morning briefing from today's calendar events and emails.
        events: list of dicts with keys title, start_label, end_label, duration_label
        emails: list of dicts with keys sender, subject (top few only)
        """
        if events:
            schedule_lines = "\n".join(
                f"- {e['start_label']}: {e['title']} ({e['duration_label']})"
                for e in events
            )
        else:
            schedule_lines = "No meetings scheduled."

        if emails:
            email_lines = "\n".join(
                f"- From {e['sender']}: \"{e['subject']}\""
                for e in emails[:5]
            )
            email_note = f"You have {len(emails)} email{'s' if len(emails) != 1 else ''} today:\n{email_lines}"
        else:
            email_note = "No new emails today."

        prompt = (
            "Generate a concise spoken morning briefing for a busy professional. "
            "Start directly with the content — no greetings. "
            "Cover the calendar schedule first, then emails. "
            "If the schedule is packed, mention the first available free block. "
            "Use natural spoken language. No bullet points, no markdown. Keep it under 120 words.\n\n"
            f"CALENDAR:\n{schedule_lines}\n\n"
            f"EMAIL:\n{email_note}"
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Atlas, a corporate personal assistant. Speak clearly and naturally."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=200,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Daily briefing unavailable: {e}"

    def compose_reply(self, original_email, dictated_message):
        """Draft a professional email reply from a user-dictated message."""
        prompt = (
            f"Write a professional email reply body only (no subject, no 'Dear X' unless appropriate).\n"
            f"Original email from: {original_email['sender']}\n"
            f"Subject: {original_email['subject']}\n"
            f"The reply should convey: {dictated_message}\n"
            f"Keep it brief, professional, and clear."
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You draft professional email replies. Return only the email body text, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return dictated_message

    def summarise_clipboard(self, text: str) -> str:
        """Return a concise spoken summary of arbitrary clipboard text."""
        prompt = f"Summarise the following text in 2-3 natural spoken sentences. No bullet points, no markdown.\n\n{text[:2000]}"
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Atlas. Summarise text concisely for voice output. No markdown."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=150,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Could not summarise: {e}"

    def improve_clipboard(self, text: str, style_hint: str = "") -> str:
        """Rewrite clipboard text to be cleaner and more professional."""
        instruction = style_hint or "more professional and clear"
        prompt = (
            f"Rewrite the following text to be {instruction}. "
            "Return ONLY the rewritten text — no explanation, no markdown, no extra lines.\n\n"
            f"{text[:2000]}"
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You rewrite text. Return only the improved text, nothing else."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=400,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return text

    def calculate(self, expression: str) -> str:
        """Evaluate any natural-language math expression and return only the answer."""
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": (
                        "You are a calculator. Given any math question in natural language, "
                        "return ONLY the numerical answer with its unit if relevant. "
                        "No explanation, no steps, no markdown.\n"
                        "Examples:\n"
                        "18% of 4500 → 810\n"
                        "square root of 144 → 12\n"
                        "15% tip on 800 → 120\n"
                        "compound interest on 10000 at 8% for 3 years → 12597.12"
                    )},
                    {"role": "user", "content": expression},
                ],
                temperature=0,
                max_tokens=60,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Couldn't calculate that: {e}"

    def convert_units(self, query: str) -> str:
        """Convert units from natural-language query, return only the result."""
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": (
                        "You convert units. Return ONLY the converted value with its unit. "
                        "Be precise. No explanation.\n"
                        "Examples:\n"
                        "5 miles to km → 8.05 km\n"
                        "100 fahrenheit in celsius → 37.78°C\n"
                        "150 pounds in kg → 68.04 kg\n"
                        "2 gallons to litres → 7.57 litres"
                    )},
                    {"role": "user", "content": query},
                ],
                temperature=0,
                max_tokens=60,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Couldn't convert that: {e}"