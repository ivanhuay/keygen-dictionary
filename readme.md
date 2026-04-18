# keygen-dictionary

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-informational)

OSINT-based password dictionary generator for authorized security testing.

Takes personal data (name, date of birth, address, domain, etc.) and produces a
targeted wordlist sorted by Shannon entropy — human-like combinations first.

> **Warning**
> For authorized use only. Only use against systems you own or have explicit written
> permission to test. The author is not responsible for misuse.

---

## Features

- Interactive mode with guided prompts (`questionary`)
- One-liner CLI mode via flags — scriptable, no prompts
- YAML config file support for repeatable target profiles
- `--config-save` to dump session inputs to YAML for reuse
- Entropy sort — low-entropy (human-like) candidates first
- Leet speak variants — default `a→4 e→3 i→1 o→0 s→5`, fully overridable via `--leet` or config
- Case variants — `.title()`, `.upper()`, `.capitalize()` generated per token
- Common suffixes seeded automatically (`!`, `123`, `1234`, `#1`, …)
- Min/max length filter to match real password policies
- Streamed output — RAM-safe even at combination level 3+
- `--dry-run` to preview token count before committing
- `-q / --quiet` for clean output when piping or scripting

---

## Installation

**From source (recommended):**

```bash
git clone https://github.com/ivanhuay/keygen-dictionary.git
cd keygen-dictionary
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

**Requirements:** Python 3.10+

---

## Usage

### Interactive mode

Run with no flags to enter guided prompts:

```bash
keygen-dictionary
```

```
keygen-dictionary v1.0.0 — leave any field empty to skip

Combination level: 2
Min password length (0 = no limit): 8
Max password length (0 = no limit): 16
Full name: John Doe
Domain URL: example.com
Birth/important date (dd-mm-yyyy): 01-01-1990
...

  Tokens collected : 169
  Est. candidates  : ~28,730
  Sample           : !, !!, #1, ...

Proceed with generation? (Y/n)
```

### CLI mode

Pass any data flag to skip interactive prompts entirely:

```bash
keygen-dictionary \
  --name "John Doe" \
  --domain example.com \
  --date 01-01-1990 \
  --level 2 \
  --min-length 8 \
  --max-length 16 \
  --output wordlist.txt \
  --entropy-sort
```

Multiple values per field:

```bash
keygen-dictionary --name "John Doe" --name "Johnny" --additional "fido" --additional "chelsea"
```

Preview without generating:

```bash
keygen-dictionary --name "John Doe" --date 01-01-1990 --dry-run
```

Custom leet substitutions and quiet output for piping:

```bash
keygen-dictionary --name "John Doe" --leet "a:@,s:$" -q --output - | head -20
```

### Config file mode

Create a YAML profile (see `config.example.yaml`):

```yaml
name:
  - "John Doe"
domain:
  - "example.com"
date:
  - "01-01-1990"
additional:
  - "fido"
level: 2
min_length: 8
max_length: 20
leet_map:           # optional — overrides default substitutions
  a: "@"
  s: "$"
```

Run against it:

```bash
keygen-dictionary --config target.yaml
```

Save current session inputs to YAML for later reuse:

```bash
keygen-dictionary --name "John Doe" --date 01-01-1990 --config-save target.yaml
```

CLI flags override config values when both are provided.

---

## Output

Candidates are written one per line to `pass.txt` (or `--output FILE`).

With `--entropy-sort` / interactive sort prompt accepted, candidates are reordered
ascending by Shannon entropy — predictable, human-chosen patterns appear first.
This improves hit rate when using the list in a sequential attack.

---

## All flags

```
usage: keygen-dictionary [-h] [--version] [--config FILE]
                         [--config-save FILE] [-q]
                         [--name NAME] [--domain DOMAIN] [--address ADDR]
                         [--date DATE] [--id ID] [--additional DATA]
                         [--level N] [--min-length N] [--max-length N]
                         [--output FILE] [--entropy-sort] [--dry-run]
                         [--leet MAP]

options:
  --config FILE      Load target data from YAML config file
  --config-save FILE Save collected inputs to YAML after loading
  -q, --quiet        Suppress all output except final line count

target data (overrides --config):
  --name NAME        Full name (repeatable)
  --domain DOMAIN    Domain URL (repeatable)
  --address ADDR     Address (repeatable)
  --date DATE        Date dd-mm-yyyy (repeatable)
  --id ID            ID number (repeatable)
  --additional DATA  Additional keyword (repeatable)

generation options:
  --level N          Combination level (default: 2)
  --min-length N     Min password length
  --max-length N     Max password length
  --output FILE      Output file (default: pass.txt)
  --entropy-sort     Sort output by entropy (RAM-heavy)
  --dry-run          Show token/candidate count without generating
  --leet MAP         Custom leet substitutions e.g. "a:@,e:3,s:$"
```

---

## Contributing

Issues and PRs welcome. See `roadmap.md` for planned work.

---

## License

MIT
