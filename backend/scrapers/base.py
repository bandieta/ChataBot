from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Listing:
    agency: str
    url: str
    title: str
    location: str
    price: Optional[int] = None
    area: Optional[float] = None
