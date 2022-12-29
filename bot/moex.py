import aiohttp
from dataclasses import dataclass
from typing import Dict, Optional
from math import inf

from logging import debug

URL = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"


@dataclass
class SecurityInfo:
    last_offer: float
    last_bid: float


def parse_offer(value: Optional[float]) -> float:
    return inf if value is None else value


def parse_bid(value: Optional[float]) -> float:
    return -inf if value is None else value


async def fetch_securities() -> Dict[str, SecurityInfo]:
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            result = (await resp.json())["marketdata"]
        columns = result["columns"]
        boardid = columns.index("BOARDID")
        lastoffer = columns.index("OFFER")
        lastbid = columns.index("BID")
        secid = columns.index("SECID")
        debug(f"Fetched {len(result['data'])} rows")
        stonks = {}
        for row in result["data"]:
            if row[boardid] != "TQBR":
                continue
            sec = row[secid]
            stonks[sec] = SecurityInfo(last_offer=parse_offer(row[lastoffer]),
                                       last_bid=parse_bid(row[lastbid]))
        return stonks


class Moex:
    def __init__(self) -> None:
        self.current = {}

    async def update(self) -> None:
        self.current = await fetch_securities()
