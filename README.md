# asystent-usos

Narzędzie do pobierania planu zajęć z USOS (format iCalendar) i liczenia statystyk
semestru: godziny per przedmiot oraz postęp (ile zajęć już się odbyło).

## Wymagania

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (zarządza venv i zależnościami)

## Instalacja

```bash
git clone <repo> && cd asystent-usos
uv sync
```

## Konfiguracja

Plan zajęć jest pobierany z prywatnego, spersonalizowanego linku USOSweb.

1. Wejdź w USOSweb → **Mój USOSweb → Plan zajęć → Eksport planu** (link `.ics`).
2. Skopiuj `.env.example` do `.env` i wklej link:

```bash
cp .env.example .env
```

```dotenv
URL=https://usosweb.put.poznan.pl/kontroler.php?_action=home/plan/eksportujPlan&...
```

Link zawiera prywatny token — `.env` i pliki `*.ics` są w `.gitignore` i nie trafiają do repozytorium.

## Użycie

Projekt dzieli się na trzy pliki, każdy z jedną odpowiedzialnością — pobieranie
uruchamiasz rzadko, raport dowolnie często.

Pobranie aktualnego planu do `plan-zajec.ics` (wymaga sieci i `.env`):

```bash
uv run python usos.py
```

Wyświetlenie planu i statystyk (działa offline, na ostatnio pobranym pliku):

```bash
uv run python main.py
```

Oba skrypty uruchamiaj z katalogu głównego projektu — ścieżka do `plan-zajec.ics`
jest względna wobec katalogu roboczego.

Przykładowy fragment wyjścia `main.py`:

```
Wczytano 216 zajęć: 01.10.2026 - 29.01.2027

--- Dziś (05.10) ---

--- Tydzień 05.10 - 11.10 ---
  Tue 06.10 15:10-16:40  LAB  Fizyka dla informatyków  [221, A1 - BM - Budowa Maszyn]
  ...

--- Godziny per przedmiot ---
    52.5 h  Fizyka dla informatyków
    ...

--- Postęp per przedmiot ---
    10.0% : Krajowe zasoby informacyjne
    ...
```

## Struktura

Podział wzdłuż osi **I/O → logika → prezentacja**:

| plik | odpowiedzialność |
| --- | --- |
| `usos.py` | pobranie pliku `.ics` z USOS (jedyne miejsce, które dotyka sieci) |
| `plan.py` | parsowanie `.ics` i statystyki — czysty moduł, bez wejścia/wyjścia i bez CLI |
| `main.py` | entry point: składa dane z `plan.py` i formatuje raport na stdout |

Pozostałe:

```
src/asystent_usos/           pakiet (na razie szkielet, entry point `asystent-usos`)
plan-zajec.ics               pobrany plan (ignorowany przez git)
todo.md                      lista zadań
```

## API modułu `plan.py`

| Element | Opis |
| --- | --- |
| `Zajecia` | jedne zajęcia: `typ` (W/CW/LAB/PRO), `przedmiot`, `start`, `koniec`, `sala`, `budynek`, `adres`, `url`, `uid`; właściwość `czas_trwania` |
| `PostepPrzedmiotu` | `odbyte` / `pozostale` w godzinach; właściwość `procent` |
| `wczytaj(plik=PLIK)` | parsuje `.ics` → lista `Zajecia` posortowana po czasie rozpoczęcia |
| `w_dniu(zajecia, dzien)` | filtruje zajęcia z jednego dnia |
| `w_zakresie(zajecia, od, do)` | filtruje zajęcia z zakresu dat (włącznie) |
| `godziny_per_przedmiot(zajecia)` | `{przedmiot: suma godzin}` |
| `postep_per_przedmiot(zajecia, teraz)` | `{przedmiot: PostepPrzedmiotu}` — podział na odbyte/pozostałe względem `teraz` |

Przykład:

```python
from datetime import datetime
import plan

zajecia = plan.wczytaj()
postepy = plan.postep_per_przedmiot(zajecia, datetime.now(plan.TZ))
print(postepy["Statystyka"].procent)
```

## Uwagi o danych z USOS

- Czasy w `.ics` są bez strefy — traktowane jako `Europe/Warsaw` (`plan.TZ`).
- Typ zajęć i nazwa przedmiotu pochodzą z pola `SUMMARY` w formacie `TYP - Nazwa`.
- Sala, budynek i link do zajęć są wyciągane z pola `DESCRIPTION`.
