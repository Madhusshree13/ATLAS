import os
import sqlite3
from datetime import datetime, date


class FinanceStore:
    EXPENSE_CATS = ["Food", "Transport", "Shopping", "Health", "Bills", "Entertainment", "Education", "Other"]
    INCOME_CATS  = ["Salary", "Freelance", "Investment", "Other Income"]

    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        c = sqlite3.connect(self.db_path)
        c.row_factory = sqlite3.Row
        return c

    def _init_db(self):
        with self._connect() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    type        TEXT NOT NULL,
                    amount      REAL NOT NULL,
                    category    TEXT,
                    description TEXT DEFAULT '',
                    tx_date     TEXT,
                    created_at  TEXT
                )
            """)

    def add(self, tx_type: str, amount: float, category: str,
            description: str = "", tx_date: str = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO transactions (type,amount,category,description,tx_date,created_at) "
                "VALUES (?,?,?,?,?,?)",
                (tx_type, abs(float(amount)), category, description,
                 tx_date or date.today().isoformat(),
                 datetime.now().isoformat()),
            )
            return cur.lastrowid

    def delete(self, tx_id: int):
        with self._connect() as c:
            c.execute("DELETE FROM transactions WHERE id=?", (tx_id,))

    def get_month(self, year: int = None, month: int = None) -> list:
        now = datetime.now()
        prefix = f"{year or now.year}-{(month or now.month):02d}"
        with self._connect() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM transactions WHERE tx_date LIKE ? ORDER BY tx_date DESC, id DESC",
                (f"{prefix}%",),
            )]

    def get_summary(self, year: int = None, month: int = None) -> dict:
        txs      = self.get_month(year, month)
        income   = sum(t["amount"] for t in txs if t["type"] == "income")
        expense  = sum(t["amount"] for t in txs if t["type"] == "expense")
        by_cat   = {}
        for t in txs:
            if t["type"] == "expense":
                by_cat[t["category"]] = by_cat.get(t["category"], 0) + t["amount"]
        return {
            "income":       income,
            "expense":      expense,
            "balance":      income - expense,
            "by_category":  dict(sorted(by_cat.items(), key=lambda x: -x[1])),
        }
