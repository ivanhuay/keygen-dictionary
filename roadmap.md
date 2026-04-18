# Roadmap

## P0 — Bug Fixes

- [x] Fix `fullName` processing gated inside `domainName` check (`processInput:144`) — names never processed if no domain entered
- [x] Fix `makeFile` opens with `'a'` (append) — reruns pile onto same file, should truncate or use unique filename
- [x] Fix `processNumbers` uses `itertools.product` generating noise (`"111"`, `"222"`) instead of meaningful substrings

## P1 — Core Improvements

- [x] **Entropy sort** — sort output ascending by Shannon entropy so human-like (predictable) combinations come first
- [x] **Min/max length filter** — skip passwords outside target range (e.g. 8–16 chars) to match real password policies
- [x] **Code cleanup & readability** — fix typos (`convination→combination`, `aditional→additional`), split large methods, add type hints, remove debug prints (e.g. `fillSimpleCollection` prints raw list), consistent naming

## P2 — Dictionary Quality

- [x] **Leet speak variants** — common substitutions: `a→4`, `e→3`, `i→1`, `o→0`, `s→5`
- [x] **Common suffixes** — append high-frequency patterns: `!`, `!!`, `123`, `1234`, `#1`, `1` to base tokens

## P3 — Performance & UX

- [x] **Stream output to file** — current approach builds full list in RAM before writing; breaks at combination level 3+
- [x] **Progress bar / ETA** — show progress during long generation runs
- [x] **Publish as pip package** — installable via `pip install keygen-dictionary`
