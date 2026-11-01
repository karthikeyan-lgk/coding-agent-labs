#!/usr/bin/env python3
"""Build the demo repo the experiments run in: "tinyledger", a small invoicing service.

Usage: python3 make_repo.py <dest-dir>

The code is generated, so no private or third-party code ends up on screen. Every module has
real, readable logic so Claude Code reads files the way it would in a normal repo. The repo gets a
project-level .claude/settings.json that turns on limit_meter.py as the status line and allows
read-only tools, so sessions never stop at a permission prompt.
"""
import json
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent

DOMAINS = {
    "customers": ("Customer", ["name", "email_domain", "country", "credit_limit"]),
    "invoices": ("Invoice", ["customer_id", "currency", "due_days", "status"]),
    "line_items": ("LineItem", ["invoice_id", "sku", "quantity", "unit_price"]),
    "payments": ("Payment", ["invoice_id", "amount", "method", "settled"]),
    "refunds": ("Refund", ["payment_id", "amount", "reason", "approved"]),
    "taxes": ("TaxRule", ["country", "rate", "category", "inclusive"]),
    "discounts": ("Discount", ["code", "percent", "max_uses", "expires_days"]),
    "reminders": ("Reminder", ["invoice_id", "channel", "attempt", "sent"]),
    "ledger": ("LedgerEntry", ["account", "debit", "credit", "memo"]),
    "reports": ("ReportRow", ["period", "revenue", "outstanding", "overdue"]),
    "webhooks": ("Webhook", ["url_host", "event", "retries", "active"]),
    "audit": ("AuditEvent", ["actor", "action", "target", "severity"]),
}

MODULE = '''"""{title} for tinyledger.

Owns the {name} table: validation, storage in memory, and the business rules other modules call.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from tinyledger.config import {const}, ROUNDING
from tinyledger.errors import NotFound, ValidationError


@dataclass
class {cls}:
    id: int
{fields}
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Raise ValidationError when a field breaks a {name} rule."""
{checks}

    def to_row(self) -> dict:
        return {{"id": self.id, {row}, "tags": list(self.tags)}}


class {cls}Store:
    """In-memory store. Swap for a database adapter in production."""

    def __init__(self) -> None:
        self._rows: dict[int, {cls}] = {{}}
        self._next_id = 1

    def add(self, item: {cls}) -> {cls}:
        item.validate()
        item.id = self._next_id
        self._rows[item.id] = item
        self._next_id += 1
        return item

    def get(self, item_id: int) -> {cls}:
        try:
            return self._rows[item_id]
        except KeyError:
            raise NotFound("{name}", item_id) from None

    def find(self, **where) -> list[{cls}]:
        """Return rows whose attributes equal every keyword given."""
        return [r for r in self._rows.values()
                if all(getattr(r, k) == v for k, v in where.items())]

    def remove(self, item_id: int) -> None:
        self.get(item_id)
        del self._rows[item_id]

    def bulk_add(self, items: Iterable[{cls}]) -> list[{cls}]:
        added = []
        for item in items:
            added.append(self.add(item))
        return added

    def __len__(self) -> int:
        return len(self._rows)


def summarize(store: {cls}Store) -> dict:
    """Counts and a numeric total used by the reports module."""
    total = 0.0
    for row in store.find():
        total += float(getattr(row, "{num}", 0) or 0)
    return {{"count": len(store), "{num}_total": round(total, ROUNDING), "limit": {const}}}


def check_limit(store: {cls}Store) -> bool:
    """True while the store holds fewer rows than {const}."""
    return len(store) < {const}
'''


def field_lines(fields):
    out = []
    for f in fields:
        typ = "float" if f in {"credit_limit", "unit_price", "amount", "rate", "percent", "debit", "credit",
                               "revenue", "outstanding", "overdue"} else \
            "int" if f.endswith(("_id", "_days", "quantity", "attempt", "retries", "max_uses", "period")) or f in {"quantity"} else \
            "bool" if f in {"settled", "approved", "inclusive", "sent", "active"} else "str"
        out.append((f, typ))
    return out


def build_module(name, cls, fields):
    typed = field_lines(fields)
    defaults = {"float": "0.0", "int": "0", "bool": "False", "str": '""'}
    flines = "\n".join(f"    {f}: {t} = {defaults[t]}" for f, t in typed)
    checks = []
    for f, t in typed:
        if t == "float":
            checks.append(f'        if self.{f} < 0:\n            raise ValidationError("{name}.{f} must not be negative")')
        elif t == "int":
            checks.append(f'        if self.{f} < 0:\n            raise ValidationError("{name}.{f} must be zero or more")')
        elif t == "str":
            checks.append(f'        if not self.{f}.strip():\n            raise ValidationError("{name}.{f} is required")')
    checks_src = "\n".join(checks) or "        return None"
    row = ", ".join(f'"{f}": self.{f}' for f, _ in typed)
    num = next((f for f, t in typed if t == "float"), typed[0][0])
    return MODULE.format(title=name.replace("_", " ").capitalize(), name=name, cls=cls, fields=flines,
                         checks=checks_src, row=row, num=num, const=f"MAX_{name.upper()}")


def main(dest: Path) -> None:
    pkg = dest / "tinyledger"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text('"""tinyledger: a small invoicing service used as a demo repo."""\n')
    consts = "\n".join(f"MAX_{n.upper()} = {500 + 37 * i}" for i, n in enumerate(DOMAINS))
    (pkg / "config.py").write_text(f'"""Limits and settings."""\n\nROUNDING = 2\nTIMEOUT_SECONDS = 42\nDEFAULT_CURRENCY = "EUR"\n{consts}\n')
    (pkg / "errors.py").write_text(
        '"""Errors shared by every module."""\n\n\nclass ValidationError(ValueError):\n    pass\n\n\n'
        'class NotFound(KeyError):\n    def __init__(self, table: str, item_id: int):\n'
        '        super().__init__(f"{table} {item_id} not found")\n')
    for name, (cls, fields) in DOMAINS.items():
        (pkg / f"{name}.py").write_text(build_module(name, cls, fields))
    (dest / "README.md").write_text("# tinyledger\n\nA small invoicing service: customers, invoices, payments, refunds, taxes and reports.\n")
    (dest / "CLAUDE.md").write_text("Python 3.12. Modules live in tinyledger/. Keep answers short.\n")
    settings = {
        "statusLine": {"type": "command", "command": f"python3 {LAB / 'limit_meter.py'}"},
        "permissions": {"allow": ["Read", "Grep", "Glob"]},
    }
    (dest / ".claude").mkdir(exist_ok=True)
    (dest / ".claude" / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run(["git", "-c", "user.name=lab", "-c", "user.email=lab@example.com", "commit", "-qm", "tinyledger"],
                   cwd=dest, check=True)
    lines = sum(len(p.read_text().splitlines()) for p in pkg.glob("*.py"))
    print(f"{dest}: {len(list(pkg.glob('*.py')))} modules, {lines} lines")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
