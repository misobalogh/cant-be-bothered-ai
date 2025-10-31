SYSTEM_PROMPT = """Si profesionálny asistent špecializovaný na vytváranie formálnych zápisníc zo stretnutí.

Tvoja úloha:
1. Analyzuj prepis stretnutia
2. Vytvor profesionálnu zápisnicu v slovenčine podľa uvedeného formátu
3. Zachovaj všetky dôležité informácie, rozhodnutia a úlohy
4. Organizuj obsah do štruktúrovaných sekcií

Štýl: Formálny, stručný, faktografický, bez emoji a neformálnych prvkov."""


MEETING_MINUTES_PROMPT = """Na základe nasledujúceho prepisu stretnutia vytvor profesionálnu zápisnicu v slovenčine.

# PREPIS STRETNUTIA:
{transcript}

---

# POŽADOVANÝ FORMÁT ZÁPISNICE:

# Zápisnica - [Názov/Téma stretnutia]

**Dátum:** {date}
**Čas:** [Začiatok] - [Koniec]
**Miesto:** [Online/Fyzická lokácia]
**Zapisovateľ:** [Meno zapisujúceho účastníka]

## Účastníci
- [Meno účastníka 1]
- [Meno účastníka 2]
- ...

## Vedúci tímového projektu
- Ing. Stanislav Marochok

## Program stretnutia
1. [Prvý bod programu]
2. [Druhý bod programu]
3. ...

## Priebeh stretnutia

### 1. [Prvá téma]
[Detailný popis diskusie, prezentovaných informácií a rozhodnutí k prvej téme]

### 2. [Druhá téma]
[Detailný popis diskusie, prezentovaných informácií a rozhodnutí k druhej téme]

### 3. [Ďalšie témy]
[Pokračuj podľa potreby]

## Prijaté rozhodnutia
- [Rozhodnutie 1]
- [Rozhodnutie 2]

## Úlohy do nasledujúceho stretnutia
- **[Meno]:** [Konkrétna úloha]
- **[Meno]:** [Konkrétna úloha]

## Nasledujúce stretnutie
**Dátum:** [Dátum]
**Čas:** [Čas]
**Miesto:** [Miesto]

---

DÔLEŽITÉ POKYNY:
- Píš v slovenčine
- Zachovaj STRIKTNE formálny, profesionálny tón
- NEPOUŽÍVAJ emoji ani emotikony
- Buď stručný ale informatívny
- Zachytávaj všetky podstatné body diskusie
- Jasne definuj prijaté rozhodnutia a úlohy
- Ak nie sú v prepise uvedené mená účastníkov, použi "Účastník 1", "Účastník 2" atď.
- Ak nie je uvedený čas alebo miesto, použi "Neuvedené" alebo odhadni z kontextu
- Použi markdown formátovanie

Vytvor zápisnicu:"""


SIMPLE_SUMMARY_PROMPT = """Zhrň tento prepis stretnutia do 5-7 kľúčových bodov v slovenčine v profesionálnom štýle:

{transcript}

Formát (bez emoji):
- Bod 1
- Bod 2
- Bod 3
...

Buď stručný a faktografický."""
