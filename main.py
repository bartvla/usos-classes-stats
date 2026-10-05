from plan import wczytaj, w_zakresie, w_dniu, godziny_per_przedmiot, postep_per_przedmiot, TZ
from datetime import datetime, timedelta

if __name__ == "__main__":
    zajecia = wczytaj()
    dzis = datetime.now(TZ).date()

    print(f"Wczytano {len(zajecia)} zajęć: "
          f"{zajecia[0].start:%d.%m.%Y} - {zajecia[-1].start:%d.%m.%Y}\n")

    print(f"--- Dziś ({dzis:%d.%m}) ---")
    for z in w_dniu(zajecia, dzis):
        print(" ", z)

    poniedzialek = dzis - timedelta(days=dzis.weekday())
    print(f"\n\n--- Tydzień {poniedzialek:%d.%m} - {poniedzialek + timedelta(days=6):%d.%m} ---\n")
    for z in w_zakresie(zajecia, poniedzialek, poniedzialek + timedelta(days=6)):
        print(" ", z)

    print("\n--- Godziny per przedmiot ---")
    godziny = godziny_per_przedmiot(zajecia)
    for przedmiot, h in sorted(godziny.items(), key=lambda p: p[1], reverse=True):
         print(f"  {h:6.1f} h  {przedmiot}")

    print("\n--- Postęp per przedmiot ---")
    teraz = datetime.now(TZ)
    postepy = postep_per_przedmiot(zajecia, teraz)
    for przedmiot, postep in sorted(postepy.items(), key=lambda p: p[1].procent, reverse=True):
        print(f"    {postep.procent:.1f}% : {przedmiot}")
