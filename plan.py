import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

TZ = ZoneInfo("Europe/Warsaw")
PLIK = Path("plan-zajec.ics")


@dataclass
class Zajecia:
    typ: str  # W, CW, LAB, PRO...
    przedmiot: str
    start: datetime
    koniec: datetime
    sala: str
    budynek: str
    adres: str
    url: str
    uid: str

    @property
    def czas_trwania(self) -> timedelta:
        return self.koniec - self.start

    def __str__(self) -> str:
        return (
            f"{self.start:%a %d.%m %H:%M}-{self.koniec:%H:%M}  "
            f"{self.typ:<4} {self.przedmiot}  [{self.sala}, {self.budynek}]"
        )

@dataclass
class PostepPrzedmiotu:
    odbyte: float
    pozostale: float

    @property
    def procent(self) -> float:
        suma_godzin = self.odbyte + self.pozostale
        if suma_godzin <= 0:
            return 0
        procent = self.odbyte / suma_godzin * 100
        return procent


def _lokalnie(wartosc) -> datetime:
    """USOS podaje czas bez strefy - traktujemy jako czas warszawski."""
    if isinstance(wartosc, datetime):
        return wartosc.astimezone(TZ) if wartosc.tzinfo else wartosc.replace(tzinfo=TZ)
    return datetime.combine(wartosc, datetime.min.time(), tzinfo=TZ)


def wczytaj(plik: Path = PLIK) -> list[Zajecia]:
    kalendarz = Calendar.from_ical(plik.read_bytes())
    wynik = []
    for wydarzenie in kalendarz.walk("VEVENT"):
        summary = str(wydarzenie.get("SUMMARY", ""))
        typ, _, przedmiot = summary.partition(" - ")
        opis = str(wydarzenie.get("DESCRIPTION", ""))
        sala = re.search(r"Sala:\s*(.+)", opis)
        linie = [w.strip() for w in opis.splitlines() if w.strip()]
        url = re.search(r"https?://\S+", opis)
        wynik.append(
            Zajecia(
                typ=typ.strip(),
                przedmiot=przedmiot.strip() or summary,
                start=_lokalnie(wydarzenie["DTSTART"].dt),
                koniec=_lokalnie(wydarzenie["DTEND"].dt),
                sala=sala.group(1).strip() if sala else "",
                budynek=linie[1] if len(linie) > 1 else "",
                adres=str(wydarzenie.get("LOCATION", "")),
                url=url.group(0) if url else "",
                uid=str(wydarzenie.get("UID", "")),
            )
        )
    return sorted(wynik, key=lambda z: z.start)


def w_dniu(zajecia: list[Zajecia], dzien: date) -> list[Zajecia]:
    return [z for z in zajecia if z.start.date() == dzien]


def w_zakresie(zajecia: list[Zajecia], od: date, do: date) -> list[Zajecia]:
    return [z for z in zajecia if od <= z.start.date() <= do]

def godziny_per_przedmiot(zajecia: list[Zajecia]) -> list[dict[str, float]]:
   godziny: dict[str, float] = {}
   for z in zajecia:
     godziny[z.przedmiot] = godziny.get(z.przedmiot, 0) + z.czas_trwania.total_seconds() / 3600
   return godziny

def postep_per_przedmiot(zajecia: list[Zajecia], teraz: datetime) -> dict[str, PostepPrzedmiotu]:
    wynik : dict[str, PostepPrzedmiotu] = {}
    for z in zajecia:
        godziny = z.czas_trwania.total_seconds() / 3600
        if z.przedmiot not in wynik:
            entry = PostepPrzedmiotu(0,0)
        else:
            entry = wynik[z.przedmiot]
        
        if z.koniec <= teraz:
            entry.odbyte += godziny
            wynik[z.przedmiot] = entry
        else:
            entry.pozostale += godziny
            wynik[z.przedmiot] = entry
    return wynik

