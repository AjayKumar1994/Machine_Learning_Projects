#!/usr/bin/env python3
"""Business AI Assistant over SQLite with sample invoicing and inventory data.

This is a complete, runnable reference implementation that demonstrates:
1) sample multi-tenant SQLite schema/data,
2) safe natural-language -> SQL routing via an intent layer,
3) tenant-aware read-only query guardrails,
4) explainable answers for business questions.

Usage:
  python business_ai_assistant.py --init-db
  python business_ai_assistant.py --tenant 1 --ask "What was my total sales last month?"
  python business_ai_assistant.py --tenant 1 --chat
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DB_PATH = Path("sample_business.db")


@dataclass(frozen=True)
class QueryResult:
    intent: str
    sql: str
    params: Tuple[Any, ...]
    rows: List[Dict[str, Any]]
    explanation: str


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema_and_data(self, seed: int = 7) -> None:
        random.seed(seed)
        with self.connect() as conn:
            cur = conn.cursor()
            cur.executescript(
                """
                PRAGMA foreign_keys = ON;

                DROP TABLE IF EXISTS invoice_items;
                DROP TABLE IF EXISTS payments;
                DROP TABLE IF EXISTS invoices;
                DROP TABLE IF EXISTS stock_movements;
                DROP TABLE IF EXISTS products;
                DROP TABLE IF EXISTS customers;
                DROP TABLE IF EXISTS users;
                DROP TABLE IF EXISTS tenants;

                CREATE TABLE tenants (
                    tenant_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );

                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    username TEXT NOT NULL,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                );

                CREATE TABLE customers (
                    customer_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    customer_name TEXT NOT NULL,
                    city TEXT,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                );

                CREATE TABLE products (
                    product_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    sku TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    cost_price REAL NOT NULL,
                    sell_price REAL NOT NULL,
                    reorder_level INTEGER NOT NULL,
                    current_stock INTEGER NOT NULL,
                    lead_time_days INTEGER NOT NULL DEFAULT 7,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                );

                CREATE TABLE invoices (
                    invoice_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    invoice_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                );

                CREATE TABLE invoice_items (
                    invoice_item_id INTEGER PRIMARY KEY,
                    invoice_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    line_total REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                );

                CREATE TABLE payments (
                    payment_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    invoice_id INTEGER NOT NULL,
                    payment_date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    method TEXT NOT NULL,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
                );

                CREATE TABLE stock_movements (
                    movement_id INTEGER PRIMARY KEY,
                    tenant_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    movement_date TEXT NOT NULL,
                    movement_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    reference_type TEXT NOT NULL,
                    reference_id INTEGER,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                );
                """
            )

            tenants = [(1, "Acme Traders"), (2, "BlueBird Retail")]
            cur.executemany("INSERT INTO tenants(tenant_id, name) VALUES(?, ?)", tenants)

            users = [
                (1, 1, "owner", "acme_owner"),
                (2, 1, "accountant", "acme_accounts"),
                (3, 2, "owner", "blue_owner"),
            ]
            cur.executemany("INSERT INTO users(user_id, tenant_id, role, username) VALUES(?, ?, ?, ?)", users)

            customer_id = 1
            product_id = 1
            invoice_id = 1
            invoice_item_id = 1
            payment_id = 1
            movement_id = 1

            categories = ["Electronics", "Stationery", "Furniture"]

            for tenant_id in (1, 2):
                for c in range(1, 11):
                    cur.execute(
                        "INSERT INTO customers(customer_id, tenant_id, customer_name, city) VALUES (?, ?, ?, ?)",
                        (customer_id, tenant_id, f"Customer_{tenant_id}_{c}", random.choice(["Pune", "Mumbai", "Delhi"])),
                    )
                    customer_id += 1

                tenant_customer_ids = [r[0] for r in cur.execute("SELECT customer_id FROM customers WHERE tenant_id=?", (tenant_id,))]

                for p in range(1, 16):
                    cost = random.randint(50, 500)
                    sell = round(cost * random.uniform(1.15, 1.8), 2)
                    current_stock = random.randint(5, 180)
                    reorder_level = random.randint(10, 40)
                    cur.execute(
                        """
                        INSERT INTO products(product_id, tenant_id, sku, product_name, category, cost_price, sell_price, reorder_level, current_stock, lead_time_days)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            product_id,
                            tenant_id,
                            f"SKU-{tenant_id}-{p:03d}",
                            f"Product_{tenant_id}_{p}",
                            random.choice(categories),
                            cost,
                            sell,
                            reorder_level,
                            current_stock,
                            random.choice([3, 5, 7, 10]),
                        ),
                    )
                    product_id += 1

                tenant_product_ids = [r[0] for r in cur.execute("SELECT product_id FROM products WHERE tenant_id=?", (tenant_id,))]

                today = dt.date.today()
                for d in range(120):
                    inv_date = today - dt.timedelta(days=d)
                    for _ in range(random.randint(0, 3)):
                        cust_id = random.choice(tenant_customer_ids)
                        due = inv_date + dt.timedelta(days=15)
                        status = random.choices(["paid", "unpaid", "partially_paid"], weights=[0.55, 0.25, 0.20])[0]
                        cur.execute(
                            """
                            INSERT INTO invoices(invoice_id, tenant_id, customer_id, invoice_date, due_date, status, total_amount)
                            VALUES (?, ?, ?, ?, ?, ?, 0)
                            """,
                            (invoice_id, tenant_id, cust_id, inv_date.isoformat(), due.isoformat(), status),
                        )

                        line_count = random.randint(1, 4)
                        inv_total = 0.0
                        for _ in range(line_count):
                            pid = random.choice(tenant_product_ids)
                            qty = random.randint(1, 10)
                            unit = cur.execute("SELECT sell_price FROM products WHERE product_id=?", (pid,)).fetchone()[0]
                            line_total = round(unit * qty, 2)
                            cur.execute(
                                """
                                INSERT INTO invoice_items(invoice_item_id, invoice_id, product_id, quantity, unit_price, line_total)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (invoice_item_id, invoice_id, pid, qty, unit, line_total),
                            )
                            invoice_item_id += 1
                            inv_total += line_total

                            cur.execute(
                                """
                                INSERT INTO stock_movements(movement_id, tenant_id, product_id, movement_date, movement_type, quantity, reference_type, reference_id)
                                VALUES (?, ?, ?, ?, 'out', ?, 'invoice', ?)
                                """,
                                (movement_id, tenant_id, pid, inv_date.isoformat(), -qty, invoice_id),
                            )
                            movement_id += 1

                        cur.execute("UPDATE invoices SET total_amount=? WHERE invoice_id=?", (round(inv_total, 2), invoice_id))

                        if status in {"paid", "partially_paid"}:
                            paid_amount = inv_total if status == "paid" else round(inv_total * random.uniform(0.2, 0.8), 2)
                            pay_date = inv_date + dt.timedelta(days=random.randint(0, 20))
                            cur.execute(
                                """
                                INSERT INTO payments(payment_id, tenant_id, invoice_id, payment_date, amount, method)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (payment_id, tenant_id, invoice_id, pay_date.isoformat(), paid_amount, random.choice(["cash", "upi", "bank"])),
                            )
                            payment_id += 1

                        invoice_id += 1

                for pid in tenant_product_ids:
                    cur.execute(
                        """
                        INSERT INTO stock_movements(movement_id, tenant_id, product_id, movement_date, movement_type, quantity, reference_type, reference_id)
                        VALUES (?, ?, ?, ?, 'in', ?, 'purchase', NULL)
                        """,
                        (movement_id, tenant_id, pid, today.isoformat(), random.randint(20, 80)),
                    )
                    movement_id += 1

            conn.commit()


class QueryGuardrails:
    FORBIDDEN = {"insert", "update", "delete", "drop", "alter", "create", "replace", "truncate", "attach", "pragma"}

    @classmethod
    def validate_sql(cls, sql: str) -> None:
        lowered = sql.lower().strip()
        if not lowered.startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")
        tokens = set(re.findall(r"[a-z_]+", lowered))
        if cls.FORBIDDEN.intersection(tokens):
            raise ValueError("Forbidden SQL operation detected.")


class BusinessAIAssistant:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def answer(self, question: str, tenant_id: int) -> QueryResult:
        q = question.strip().lower()
        intent, sql, params, explanation = self._plan(q, tenant_id)
        QueryGuardrails.validate_sql(sql)
        rows = [dict(r) for r in self.conn.execute(sql, params).fetchall()]
        return QueryResult(intent, sql, params, rows, explanation)

    def _plan(self, question: str, tenant_id: int) -> Tuple[str, str, Tuple[Any, ...], str]:
        today = dt.date.today()
        month_start = today.replace(day=1)
        prev_month_end = month_start - dt.timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        if "total sales" in question and "last month" in question:
            return (
                "sales_last_month",
                """
                SELECT COALESCE(ROUND(SUM(total_amount), 2), 0) AS total_sales
                FROM invoices
                WHERE tenant_id = ?
                  AND invoice_date >= ?
                  AND invoice_date <= ?
                """,
                (tenant_id, prev_month_start.isoformat(), prev_month_end.isoformat()),
                f"Computed sum of invoice totals for last month ({prev_month_start} to {prev_month_end}).",
            )

        if "top" in question and "customer" in question:
            m = re.search(r"top\s+(\d+)", question)
            top_n = int(m.group(1)) if m else 5
            return (
                "top_customers",
                """
                SELECT c.customer_name, ROUND(SUM(i.total_amount), 2) AS revenue
                FROM invoices i
                JOIN customers c ON c.customer_id = i.customer_id
                WHERE i.tenant_id = ?
                GROUP BY c.customer_id, c.customer_name
                ORDER BY revenue DESC
                LIMIT ?
                """,
                (tenant_id, top_n),
                f"Ranked customers by summed invoice revenue and returned top {top_n}.",
            )

        if ("low stock" in question) or ("stock out" in question) or ("stockout" in question):
            return (
                "low_stock",
                """
                SELECT sku, product_name, current_stock, reorder_level, lead_time_days
                FROM products
                WHERE tenant_id = ?
                  AND current_stock <= reorder_level
                ORDER BY (reorder_level - current_stock) DESC, current_stock ASC
                """,
                (tenant_id,),
                "Returned products where stock is at or below reorder level.",
            )

        if "overdue" in question and "invoice" in question:
            return (
                "overdue_invoices",
                """
                SELECT i.invoice_id, c.customer_name, i.invoice_date, i.due_date, i.total_amount,
                       COALESCE(SUM(p.amount), 0) AS paid_amount,
                       ROUND(i.total_amount - COALESCE(SUM(p.amount), 0), 2) AS outstanding
                FROM invoices i
                JOIN customers c ON c.customer_id = i.customer_id
                LEFT JOIN payments p ON p.invoice_id = i.invoice_id
                WHERE i.tenant_id = ?
                  AND date(i.due_date) < date('now')
                GROUP BY i.invoice_id, c.customer_name, i.invoice_date, i.due_date, i.total_amount
                HAVING outstanding > 0
                ORDER BY outstanding DESC
                """,
                (tenant_id,),
                "Listed overdue invoices with remaining outstanding amount.",
            )

        if ("unpaid" in question and "invoice" in question) or ("receivable" in question):
            return (
                "accounts_receivable_summary",
                """
                SELECT COUNT(*) AS unpaid_invoice_count,
                       ROUND(SUM(i.total_amount - COALESCE(p.paid, 0)), 2) AS total_receivable
                FROM invoices i
                LEFT JOIN (
                    SELECT invoice_id, SUM(amount) AS paid
                    FROM payments
                    WHERE tenant_id = ?
                    GROUP BY invoice_id
                ) p ON p.invoice_id = i.invoice_id
                WHERE i.tenant_id = ?
                  AND (i.total_amount - COALESCE(p.paid, 0)) > 0
                """,
                (tenant_id, tenant_id),
                "Calculated unpaid invoice count and total receivable outstanding.",
            )

        return (
            "fallback",
            """
            SELECT 'I can help with total sales, top customers, low stock, overdue invoices, and receivables.' AS message
            """,
            tuple(),
            "Fallback answer because question does not match supported intents.",
        )


def pretty_print(result: QueryResult) -> None:
    print("\n=== Assistant Response ===")
    print(f"Intent: {result.intent}")
    print(f"Explanation: {result.explanation}")
    print("SQL:")
    print(result.sql.strip())
    print(f"Params: {result.params}")
    print("Result:")
    print(json.dumps(result.rows, indent=2, default=str))


def chat_loop(conn: sqlite3.Connection, tenant_id: int) -> None:
    assistant = BusinessAIAssistant(conn)
    print("Type your question (or 'exit' to quit):")
    while True:
        q = input("you> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        res = assistant.answer(q, tenant_id=tenant_id)
        pretty_print(res)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Business AI assistant demo over SQLite")
    p.add_argument("--db", type=Path, default=DB_PATH, help="SQLite db path")
    p.add_argument("--init-db", action="store_true", help="Create schema and load sample data")
    p.add_argument("--tenant", type=int, default=1, help="Tenant id for row-level scoping")
    p.add_argument("--ask", type=str, help="Single question to ask")
    p.add_argument("--chat", action="store_true", help="Interactive chat mode")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dbm = DatabaseManager(args.db)

    if args.init_db:
        dbm.init_schema_and_data()
        print(f"Database initialized at: {args.db}")

    with dbm.connect() as conn:
        if args.ask:
            res = BusinessAIAssistant(conn).answer(args.ask, tenant_id=args.tenant)
            pretty_print(res)

        if args.chat:
            chat_loop(conn, tenant_id=args.tenant)


if __name__ == "__main__":
    main()
