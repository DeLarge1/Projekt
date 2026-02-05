# AI Study Response Quality Checker + Explain-My-Prompt

Dva praktična AI alata u jednom repozitoriju:
1. **AI Study Response Quality Checker** – analizira tekstualne odgovore iz studija/surveys i označava low-effort, copy-paste i moguće kontradikcije.
2. **Explain-My-Prompt** – objašnjava zašto prompt radi/ne radi, koje implicitne instrukcije nosi i gdje gubiš kontrolu nad outputom.

## Problem
Istraživači i PM timovi često dobiju veliki broj nekvalitetnih odgovora (kratki, copy-paste, kontradiktorni), a prompt engineering se koristi bez jasnog razumijevanja šta prompt zapravo signalizira modelu.

## Why it matters
- Loš kvalitet odgovora vodi do loših zaključaka.
- Ručno čišćenje data quality problema troši mnogo vremena.
- Bolje razumijevanje prompta znači konzistentnije AI rezultate.
- Neutralan i etički pristup: alat ne "kažnjava" učesnike, već označava sumnjive obrasce za ljudski pregled.

## How it works
### 1) Quality Checker
Ulaz: CSV sa kolonom odgovora.

Heuristike + embedding-ish pristup:
- **Low-effort**: premalo tokena, poznati low-effort patterni, visok repetition ratio.
- **Copy-paste**: TF-IDF + cosine similarity između odgovora.
- **Contradictions**: jednostavna detekcija suprotnih tvrdnji kroz parove termina (npr. "always" + "never").

Izlaz:
- `quality_score` (0-100)
- `flags` (`low_effort`, `possible_copy_paste`, `possible_contradiction`)

### 2) Explain-My-Prompt
Ulaz: prompt tekst.

Analiza:
- prisutnost role/context signala,
- prisutnost constraints,
- prisutnost formatnih očekivanja,
- rizici gubitka kontrole (vague terms, nejasan format, prekratak prompt).

Izlaz:
- `why_it_works`
- `why_it_might_fail`
- `implicit_instructions`
- `control_risks`

## Example input/output
### Quality checker
```bash
python src/main.py quality-check \
  --input data/synthetic_responses.csv \
  --text-column response \
  --output examples/scored_responses.csv
```

Dobijeni CSV sadrži dodatne kolone `quality_score` i `flags`.

### Explain-my-prompt
```bash
python src/main.py explain-prompt \
  --prompt "You are a strict reviewer. Return JSON with 3 bullets."
```

Output je JSON sa objašnjenjem prompt kvaliteta.

## Ethical considerations
- Ovaj alat je **assistive**, ne konačni sudija kvaliteta.
- Flagovi su indikatori za ljudski audit, ne automatsko izbacivanje učesnika.
- Heuristike mogu imati false positives/negatives, posebno za kratke ali legitimne odgovore.
- Preporučuje se kalibracija thresholda po tipu studije i jeziku.

## Repo struktura
```text
.
├── src/
│   ├── main.py
│   ├── prompt_explainer.py
│   └── quality_checker.py
├── data/
│   └── synthetic_responses.csv
├── examples/
│   └── example_prompt.txt
├── tests/
│   └── test_toolkit.py
├── README.md
└── requirements.txt
```

## Instalacija
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Testiranje
```bash
python -m pytest -q
```
