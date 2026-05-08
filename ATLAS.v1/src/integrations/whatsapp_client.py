"""
whatsapp_client.py — Send WhatsApp messages via WhatsApp Web deep link.

How it works:
  Opens https://web.whatsapp.com/send?phone=<number>&text=<message>
  WhatsApp Web must be open and logged in; the user presses Enter to send.

Contacts live in data/contacts.json:
  { "priya": "+919876543210", "mom": "+919123456789" }
Phone numbers must be in international format (with country code, no spaces).
"""

import os
import json
import webbrowser
from urllib.parse import quote as _q


class WhatsAppClient:
    def __init__(self, contacts_path: str):
        self._path = contacts_path
        if not os.path.exists(contacts_path):
            os.makedirs(os.path.dirname(contacts_path), exist_ok=True)
            with open(contacts_path, "w") as f:
                json.dump({}, f, indent=2)

    def _contacts(self) -> dict:
        try:
            with open(self._path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _resolve(self, name: str) -> str:
        """Return phone number for name, or None if not found (case-insensitive, partial match)."""
        contacts = self._contacts()
        name_lower = name.lower().strip()
        # Exact match first
        if name_lower in contacts:
            return contacts[name_lower]
        # Partial match
        for k, v in contacts.items():
            if name_lower in k.lower() or k.lower() in name_lower:
                return v
        return None

    def send(self, name: str, message: str) -> tuple:
        """
        Open WhatsApp Web pre-composed to `name` with `message`.
        Returns (success: bool, feedback: str).
        """
        phone = self._resolve(name)
        if not phone:
            return (
                False,
                f"No contact found for '{name}'. "
                f"Add them to data/contacts.json as {{\"name\": \"+91XXXXXXXXXX\"}}.",
            )

        # Strip non-digit characters except leading +
        phone = "".join(c for c in phone if c.isdigit())
        url = f"https://web.whatsapp.com/send?phone={phone}&text={_q(message)}"
        webbrowser.open(url)
        return True, f"WhatsApp opened for {name}. Press Enter in the browser to send."

    def add_contact(self, name: str, phone: str):
        """Programmatically add a contact."""
        contacts = self._contacts()
        contacts[name.lower().strip()] = phone.strip()
        with open(self._path, "w") as f:
            json.dump(contacts, f, indent=2)
        print(f"[WhatsApp] Contact saved: {name} → {phone}")
