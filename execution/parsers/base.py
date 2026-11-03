"""Parser interface and the Transaction schema every parser must return."""
from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from email.message import EmailMessage
from typing import Literal

TxType = Literal["income", "expense", "transfer"]
TX_TYPES: tuple[str, ...] = ("income", "expense", "transfer")


@dataclass(frozen=True)
class Transaction:
    message_id: str
    sender: str
    occurred_at: datetime        # timezone-aware
    type: TxType
    amount: Decimal              # never float
    currency: str                # ISO 4217, e.g. "USD"
    card_or_account: str | None  # masked, e.g. "VISA ••1234"
    merchant: str | None
    category: str = "Uncategorized"
    raw_snippet: str = ""

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")
        if self.type not in TX_TYPES:
            raise ValueError(f"type must be one of {TX_TYPES}, got {self.type!r}")
        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be Decimal, never float")
        if self.amount < 0:
            raise ValueError("amount must be positive; direction is given by type")
        if not re.fullmatch(r"[A-Z]{3}", self.currency):
            raise ValueError(f"currency must be an ISO 4217 code, got {self.currency!r}")

    def fingerprint(self) -> str:
        """Dedup key across emails: amount + minute + card last-4 + merchant."""
        last4 = re.sub(r"\D", "", self.card_or_account or "")[-4:]
        merchant = re.sub(r"\s+", " ", (self.merchant or "").strip().lower())
        key = "|".join([
            f"{self.amount:.2f}", self.currency,
            self.occurred_at.strftime("%Y-%m-%dT%H:%M%z"), last4, merchant,
        ])
        return hashlib.sha256(key.encode()).hexdigest()[:32]


def mask_card(text: str | None, brand: str | None = None) -> str | None:
    """Keep only the last 4 digits of any card/account number."""
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    if len(digits) < 4:
        return None
    return f"{brand + ' ' if brand else ''}••{digits[-4:]}"


class Parser(ABC):
    """One subclass per sender. Return [] for promotional or non-transaction emails."""

    slug: str = ""                 # matches config/senders.yaml
    senders: tuple[str, ...] = ()  # addresses or @domains this parser handles

    def matches(self, from_address: str) -> bool:
        addr = from_address.lower()
        return any(addr == s or (s.startswith("@") and addr.endswith(s)) for s in self.senders)

    @abstractmethod
    def parse(self, msg: EmailMessage) -> list[Transaction]:
        """Extract transactions. Raise ValueError if the template is unrecognized."""
