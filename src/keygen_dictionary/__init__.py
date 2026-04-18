#!/usr/bin/python3
__version__ = "1.0.0"

import argparse
import itertools
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import questionary
import yaml


class DictionaryMaker:
    def __init__(self):
        self.additional_data: list[str] = []
        self.tokens: list[str] = ["admin", "adm", ".", "-", "_", "@"]
        self.combination_level: int = 2
        self.min_length: int = 0
        self.max_length: int = 0
        self.domain_name: list[str] = []
        self.full_name: list[str] = []
        self.address: list[str] = []
        self.important_date: list[str] = []
        self.identification: list[str] = []
        self.quiet: bool = False
        self._leet_table: dict[int, str] = str.maketrans("aeios", "43105")
        self._seed_years()
        self._seed_suffixes()

    _COMMON_SUFFIXES = ["!", "!!", "123", "1234", "#1", "1", "01", "99", "2000"]

    def _seed_years(self) -> None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 10, current_year)]
        years_short = [str(y)[-2:] for y in range(current_year - 10, current_year)]
        self.tokens.extend(years)
        self.tokens.extend(years_short)

    def _seed_suffixes(self) -> None:
        self.tokens.extend(self._COMMON_SUFFIXES)

    def set_leet_map(self, mapping: dict[str, str]) -> None:
        self._leet_table = str.maketrans(
            "".join(mapping.keys()),
            "".join(mapping.values()),
        )

    # ── Input ────────────────────────────────────────────────────────────────

    def interactive(self) -> None:
        print(f"keygen-dictionary v{__version__} — leave any field empty to skip\n")
        self._get_inputs()
        self._process_input()
        if not self._confirm_tokens():
            print("Aborted.")
            return
        self._generate_dictionary()

    def _get_inputs(self) -> None:
        def ask_multi(label: str, hint: str = "") -> list[str]:
            prompt = label + (f" ({hint})" if hint else "")
            raw = questionary.text(prompt + ":").ask()
            if not raw or not raw.strip():
                return []
            return [v.strip() for v in raw.split(",") if v.strip()]

        level_raw = questionary.text(
            "Combination level:",
            default="2",
            validate=lambda v: v.isdigit() and int(v) >= 1 or "Must be a positive integer",
        ).ask()
        self.combination_level = int(level_raw) if level_raw else 2

        min_raw = questionary.text("Min password length (0 = no limit):", default="0").ask()
        self.min_length = int(min_raw) if min_raw and min_raw.strip() != "0" else 0

        max_raw = questionary.text("Max password length (0 = no limit):", default="0").ask()
        self.max_length = int(max_raw) if max_raw and max_raw.strip() != "0" else 0

        self.full_name       = ask_multi("Full name",           "comma-separated if multiple")
        self.domain_name     = ask_multi("Domain URL")
        self.address         = ask_multi("Address")
        self.important_date  = ask_multi("Birth/important date","dd-mm-yyyy")
        self.identification  = ask_multi("ID number")
        self.additional_data = ask_multi("Additional keywords", "comma-separated")

    def _confirm_tokens(self) -> bool:
        tokens = self._dedup(self.tokens)
        n = len(tokens)
        total = sum(n ** i for i in range(1, self.combination_level + 1))
        sample = ", ".join(tokens[:12]) + ("..." if n > 12 else "")
        print(f"\n  Tokens collected : {n:,}")
        print(f"  Est. candidates  : ~{total:,}")
        print(f"  Sample           : {sample}\n")
        return questionary.confirm("Proceed with generation?", default=True).ask()

    def load_from_args(self, args: argparse.Namespace) -> None:
        if args.name:
            self.full_name = args.name
        if args.domain:
            self.domain_name = args.domain
        if args.address:
            self.address = args.address
        if args.date:
            self.important_date = args.date
        if args.id:
            self.identification = args.id
        if args.additional:
            self.additional_data = args.additional
        if args.level:
            self.combination_level = args.level
        if args.min_length:
            self.min_length = args.min_length
        if args.max_length:
            self.max_length = args.max_length
        if args.leet:
            self.set_leet_map(_parse_leet_arg(args.leet))

    def load_from_config(self, path: str) -> None:
        data = yaml.safe_load(Path(path).read_text())
        if not isinstance(data, dict):
            raise ValueError(f"Invalid config: {path}")
        self.full_name       = data.get("name", [])
        self.domain_name     = data.get("domain", [])
        self.address         = data.get("address", [])
        self.important_date  = data.get("date", [])
        self.identification  = data.get("id", [])
        self.additional_data = data.get("additional", [])
        if "level" in data:
            self.combination_level = int(data["level"])
        if "min_length" in data:
            self.min_length = int(data["min_length"])
        if "max_length" in data:
            self.max_length = int(data["max_length"])
        if "leet_map" in data:
            self.set_leet_map({str(k): str(v) for k, v in data["leet_map"].items()})

    def save_config(self, path: str) -> None:
        data: dict = {}
        if self.full_name:
            data["name"] = self.full_name
        if self.domain_name:
            data["domain"] = self.domain_name
        if self.address:
            data["address"] = self.address
        if self.important_date:
            data["date"] = self.important_date
        if self.identification:
            data["id"] = self.identification
        if self.additional_data:
            data["additional"] = self.additional_data
        data["level"] = self.combination_level
        if self.min_length:
            data["min_length"] = self.min_length
        if self.max_length:
            data["max_length"] = self.max_length
        Path(path).write_text(yaml.dump(data, default_flow_style=False))
        print(f"Config saved to {path}.")

    # ── Token processors ─────────────────────────────────────────────────────

    def _process_numbers(self, text: str) -> list[str]:
        tokens = []
        for number in (s for s in text.split() if s.isdigit()):
            for i in range(1, len(number) + 1):
                tokens.append(number[:i])
                if number[i:]:
                    tokens.append(number[i:])
        return tokens

    def _process_str(self, text: str) -> list[str]:
        words = [s for s in text.split() if not s.isdigit()]
        return words + [text, "".join(text.split())]

    def _process_name(self, text: str) -> list[str]:
        tokens = self._process_str(text)
        words = [s for s in text.split() if not s.isdigit()]
        for word in words:
            tokens.append(word[0])
            tokens.append(word[0].upper())
        for combo in itertools.product(tokens, repeat=2):
            tokens.append("".join(combo))
        return self._dedup(tokens)

    def _process_domain(self, text: str) -> list[str]:
        return [text] + text.split(".")

    def _process_address(self, text: str) -> list[str]:
        tokens = [text] + text.split() + ["".join(text.split())]
        tokens.extend(self._process_numbers(text))
        tokens.extend(self._process_str(text))
        return tokens

    def _process_date(self, text: str) -> list[str]:
        tokens: list[str] = []
        if "/" in text:
            tokens.extend(text.split("/"))
        if "-" in text:
            tokens.extend(text.split("-"))

        if not tokens:
            return tokens

        if len(tokens) == 3 and len(tokens[2]) == 4:
            tokens.append(tokens[2][:2])
            tokens.append(tokens[2][2:])

        for combo in itertools.combinations(tokens, 3):
            tokens.append("".join(combo))

        self._log(f"Date combinations: {len(tokens)}.")
        return self._dedup(tokens)

    def _process_identification(self, text: str) -> list[str]:
        numbers = [text] if len(text) == 1 else [s for s in text.split() if s.isdigit()]
        tokens: list[str] = []
        for number in numbers:
            if len(number) == 1:
                tokens.append(number)
            else:
                for i in range(1, len(number)):
                    tokens.append(number[:i])
        return self._dedup(tokens)

    # ── Processing pipeline ───────────────────────────────────────────────────

    def _process_input(self) -> None:
        self._log("Starting processing...")
        processors = [
            (self.domain_name,    "domain name",     self._process_domain),
            (self.full_name,      "full name",        self._process_name),
            (self.address,        "address",          self._process_address),
            (self.additional_data,"additional data",  self._process_str),
            (self.important_date, "dates",            self._process_date),
            (self.identification, "identification",   self._process_identification),
        ]
        for values, label, fn in processors:
            if values:
                self._log(f"Processing {label}...")
                for value in values:
                    self.tokens.extend(fn(value))

        existing = set(self.tokens)
        case_variants = []
        for t in self.tokens:
            for variant in (t.title(), t.upper(), t.capitalize()):
                if variant not in existing:
                    case_variants.append(variant)
                    existing.add(variant)
        self.tokens.extend(case_variants)

        self._apply_leet()
        self._green_print("Done")

    def _apply_leet(self) -> None:
        existing = set(self.tokens)
        leet_variants = []
        for token in self.tokens:
            variant = token.lower().translate(self._leet_table)
            if variant != token.lower() and variant not in existing:
                leet_variants.append(variant)
                existing.add(variant)
        self.tokens.extend(leet_variants)
        self._log(f"Leet variants added: {len(leet_variants)}.")

    # ── Dictionary generation ─────────────────────────────────────────────────

    @staticmethod
    def _shannon_entropy(s: str) -> float:
        if not s:
            return 0.0
        freq = Counter(s)
        n = len(s)
        return -sum((c / n) * math.log2(c / n) for c in freq.values())

    def _passes_length_filter(self, s: str) -> bool:
        if self.min_length and len(s) < self.min_length:
            return False
        if self.max_length and len(s) > self.max_length:
            return False
        return True

    def dry_run(self) -> None:
        self._process_input()
        tokens = self._dedup(self.tokens)
        n = len(tokens)
        total = sum(n ** i for i in range(1, self.combination_level + 1))
        print(f"Tokens:          {n:,}")
        print(f"Level:           {self.combination_level}")
        print(f"Est. candidates: ~{total:,}")
        if self.min_length or self.max_length:
            lo = self.min_length or "—"
            hi = self.max_length or "—"
            print(f"Length filter:   {lo}–{hi}")

    def _generate_dictionary(
        self,
        output: str = "pass.txt",
        entropy_sort: bool | None = None,
    ) -> None:
        tokens = self._dedup(self.tokens)
        n = len(tokens)
        total = sum(n ** i for i in range(1, self.combination_level + 1))
        self._log(f"Making combinations from {n} tokens (~{total:,} candidates)...")

        seen: set[str] = set()
        written = 0
        processed = 0

        with open(output, "w") as f:
            for level in range(1, self.combination_level + 1):
                self._log(f"Starting level {level}...")
                for combo in itertools.product(tokens, repeat=level):
                    processed += 1
                    candidate = "".join(combo)
                    if candidate not in seen and self._passes_length_filter(candidate):
                        seen.add(candidate)
                        f.write(candidate + "\n")
                        written += 1
                    if not self.quiet and processed % 50_000 == 0:
                        pct = processed / total * 100
                        sys.stdout.write(f"\r  {processed:,}/{total:,} ({pct:.1f}%) — {written:,} written")
                        sys.stdout.flush()
                if not self.quiet:
                    sys.stdout.write("\n")
                self._green_print(f"Level {level}: done")

        # always print final count even in quiet mode
        print(f"Wrote {written:,} lines to {output}.")

        if entropy_sort is None:
            raw = input("Sort by entropy? Loads all lines into RAM (y/N): ").strip().lower()
            entropy_sort = raw == "y"

        if entropy_sort:
            self._entropy_sort_file(output)

    def _entropy_sort_file(self, path: str) -> None:
        self._log("Loading file for entropy sort...")
        with open(path) as f:
            lines = [line.rstrip("\n") for line in f]
        self._log(f"Sorting {len(lines):,} lines...")
        lines.sort(key=self._shannon_entropy)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        self._green_print("Entropy sort done.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _dedup(self, items: list[str]) -> list[str]:
        return sorted(set(items))

    def _log(self, text: str) -> None:
        if not self.quiet:
            print(text)

    def _green_print(self, text: str) -> None:
        if not self.quiet:
            print(f"\033[92m{text} \u2713\033[0m")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_leet_arg(raw: str) -> dict[str, str]:
    mapping = {}
    for pair in raw.split(","):
        if ":" not in pair:
            raise argparse.ArgumentTypeError(f"Invalid leet pair: {pair!r} (expected 'char:sub')")
        k, v = pair.split(":", 1)
        mapping[k.strip()] = v.strip()
    return mapping


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="keygen-dictionary",
        description="OSINT-based password dictionary generator for authorized security testing.",
        epilog="Omit all data flags to enter interactive mode.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config",      metavar="FILE", help="Load target data from YAML config file")
    parser.add_argument("--config-save", metavar="FILE", help="Save collected inputs to YAML after loading")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all output except final line count")

    data = parser.add_argument_group("target data (overrides --config)")
    data.add_argument("--name",       metavar="NAME",   action="append", help="Full name (repeatable)")
    data.add_argument("--domain",     metavar="DOMAIN", action="append", help="Domain URL (repeatable)")
    data.add_argument("--address",    metavar="ADDR",   action="append", help="Address (repeatable)")
    data.add_argument("--date",       metavar="DATE",   action="append", help="Date dd-mm-yyyy (repeatable)")
    data.add_argument("--id",         metavar="ID",     action="append", help="ID number (repeatable)")
    data.add_argument("--additional", metavar="DATA",   action="append", help="Additional keyword (repeatable)")

    gen = parser.add_argument_group("generation options")
    gen.add_argument("--level",      type=int, default=None, metavar="N",    help="Combination level (default: 2)")
    gen.add_argument("--min-length", type=int, default=None, metavar="N",    help="Min password length")
    gen.add_argument("--max-length", type=int, default=None, metavar="N",    help="Max password length")
    gen.add_argument("--output",     default="pass.txt",     metavar="FILE", help="Output file (default: pass.txt)")
    gen.add_argument("--entropy-sort", action="store_true",                  help="Sort output by entropy (RAM-heavy)")
    gen.add_argument("--dry-run",    action="store_true",                    help="Show token/candidate count without generating")
    gen.add_argument("--leet",       metavar="MAP",                          help="Custom leet map e.g. 'a:4,e:3,s:$'")

    return parser.parse_args()


def _has_data_args(args: argparse.Namespace) -> bool:
    return any([args.name, args.domain, args.address, args.date, args.id, args.additional])


def main() -> None:
    try:
        args = _parse_args()
        maker = DictionaryMaker()
        maker.quiet = args.quiet

        if args.config:
            maker.load_from_config(args.config)
        if _has_data_args(args):
            maker.load_from_args(args)

        if args.config_save:
            maker.save_config(args.config_save)

        if args.config or _has_data_args(args):
            if args.dry_run:
                maker.dry_run()
            else:
                maker._process_input()
                maker._generate_dictionary(
                    output=args.output,
                    entropy_sort=args.entropy_sort or None,
                )
        else:
            maker.interactive()

    except KeyboardInterrupt:
        print("\n\nKeygen interrupted. Bye!")


if __name__ == "__main__":
    main()
