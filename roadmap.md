# Roadmap

---

## v1.0.0 — Completed

### Bug Fixes
- [x] Fix `full_name` processing gated inside `domain_name` check — names never processed if no domain entered
- [x] Fix `makeFile` append mode — reruns pile onto same file
- [x] Fix `processNumbers` using `itertools.product` generating noisy digit combos instead of meaningful substrings

### Core Improvements
- [x] **Entropy sort** — output sorted ascending by Shannon entropy (human-like patterns first), opt-in to avoid RAM blowup
- [x] **Min/max length filter** — skip candidates outside target range to match real password policies
- [x] **Code cleanup** — type hints, snake_case, data-driven processor loop, removed debug prints and unused imports

### Dictionary Quality
- [x] **Leet speak variants** — `a→4`, `e→3`, `i→1`, `o→0`, `s→5` applied post-processing
- [x] **Common suffixes** — `!`, `!!`, `123`, `1234`, `#1`, `01`, `99`, `2000` seeded as base tokens

### Performance & Packaging
- [x] **Stream output to file** — direct write per candidate, no full list in RAM
- [x] **Progress bar** — inline `\r` counter showing processed/total/written
- [x] **pip package** — `pyproject.toml` with `keygen-dictionary` entrypoint

---

## v1.1.0 — Planned

### Project Structure
- [x] **Move to `src/` layout** — `src/keygen_dictionary/` package; update `pyproject.toml` find-packages path and entrypoint

### CLI Args
- [x] **`argparse` one-liner mode** — skip interactive prompts entirely when args provided:
  ```
  keygen-dictionary --name "John Doe" --date 01-01-1990 --domain example.com \
    --level 2 --min-length 8 --max-length 16 --output wordlist.txt
  ```
- [x] **`--dry-run` flag** — show token count and estimated candidate count without generating
- [x] **`--output` flag** — custom output filename (default: `pass.txt`)
- [x] **`--version` flag** — print version and exit

### Input UX
- [ ] **Config file support** — load inputs from YAML/JSON profile; useful for rerunning same target
  ```
  keygen-dictionary --config target.yaml
  ```
- [ ] **Interactive mode polish** — replace raw `input()` with arrow-key navigation, inline validation, and clear field descriptions (consider `questionary` or `InquirerPy`)
- [ ] **Confirm step** — show collected tokens before generation; let user abort or adjust

### Docs
- [ ] **Rewrite README** — add badges (Python version, license), usage examples for both interactive and CLI modes, output format explanation, ethical use disclaimer prominently at top
- [ ] **Add `--help` examples** in README

### Tests
- [ ] **Unit tests for processors** — `_process_name`, `_process_date`, `_process_numbers`, `_process_identification` each have edge cases worth pinning (empty input, single char, date format variants)
- [ ] **Entropy sort correctness** — assert `"password"` ranks lower than `"xK9@mN2"`
- [ ] **Length filter** — assert candidates outside min/max are excluded
- [ ] **Leet variants** — assert `"admin"` → `"4dm1n"`, no duplicates added
- [ ] **Integration test** — run full pipeline with fixture inputs, assert output file non-empty and sorted by entropy when opted in
- [ ] **CI** — GitHub Actions workflow: run tests on push to `master` + PRs

### Extras (suggestions)
- [ ] **`--config-save` flag** — dump current session inputs to YAML for reuse
- [ ] **Quiet mode (`-q`)** — suppress all output except final line count (useful when piping)
- [ ] **Custom leet map** — let user override substitutions via config or flag
- [ ] **Case variants** — beyond `.title()`: add `.upper()` and `.capitalize()` per token
