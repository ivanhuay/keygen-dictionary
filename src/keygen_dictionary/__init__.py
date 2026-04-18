#!/usr/bin/python3
__version__ = "1.0.0"

import argparse
import itertools
import math
import sys
from collections import Counter
from datetime import datetime


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
        self._seed_years()
        self._seed_suffixes()

    _LEET_TABLE = str.maketrans("aeios", "43105")

    _COMMON_SUFFIXES = ["!", "!!", "123", "1234", "#1", "1", "01", "99", "2000"]

    def _seed_years(self) -> None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 10, current_year)]
        years_short = [str(y)[-2:] for y in range(current_year - 10, current_year)]
        self.tokens.extend(years)
        self.tokens.extend(years_short)

    def _seed_suffixes(self) -> None:
        self.tokens.extend(self._COMMON_SUFFIXES)

    # ── Input ────────────────────────────────────────────────────────────────

    def interactive(self) -> None:
        print("Welcome human, Please answer the following questions...")
        self._get_inputs()
        self._process_input()
        self._generate_dictionary()

    def _get_inputs(self) -> None:
        print("Usage: leave empty to skip a field.")
        raw = input("Combination level (2 recommended): ")
        if raw.strip():
            self.combination_level = int(raw)

        raw = input("Min password length (0 = no limit): ")
        if raw.strip():
            self.min_length = int(raw)

        raw = input("Max password length (0 = no limit): ")
        if raw.strip():
            self.max_length = int(raw)

        self._ask("Domain URL?", "domain_name")
        self._ask("Address?", "address")
        self._ask("Full name?", "full_name")
        self._ask("Birthdate or important date? (dd-mm-yyyy)", "important_date")
        self._ask("Identifier or ID number?", "identification")
        self._ask("Additional data?", "additional_data")

    def _ask(self, question: str, attr: str) -> None:
        values: list[str] = []
        while True:
            answer = input(f"{question} (empty = next field): ").strip()
            if not answer:
                break
            values.append(answer)
        setattr(self, attr, values)

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

        print(f"Date combinations: {len(tokens)}.")
        return self._dedup(tokens)

    def _process_identification(self, text: str) -> list[str]:
        numbers = [text] if len(text) == 1 else [s for s in text.split() if s.isdigit()]
        tokens: list[str] = []
        for number in numbers:
            for i in range(1, len(number)):
                tokens.append(number[:i])
        return self._dedup(tokens)

    # ── Processing pipeline ───────────────────────────────────────────────────

    def _process_input(self) -> None:
        print("Starting processing...")
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
                print(f"Processing {label}...")
                for value in values:
                    self.tokens.extend(fn(value))

        title_variants = [t.title() for t in self.tokens if t.title() not in self.tokens]
        self.tokens.extend(title_variants)
        self._apply_leet()
        self._green_print("Done")

    def _apply_leet(self) -> None:
        existing = set(self.tokens)
        leet_variants = []
        for token in self.tokens:
            variant = token.lower().translate(self._LEET_TABLE)
            if variant != token.lower() and variant not in existing:
                leet_variants.append(variant)
                existing.add(variant)
        self.tokens.extend(leet_variants)
        print(f"Leet variants added: {len(leet_variants)}.")

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
        print(f"Tokens:        {n:,}")
        print(f"Level:         {self.combination_level}")
        print(f"Est. candidates: ~{total:,}")
        if self.min_length or self.max_length:
            lo = self.min_length or "—"
            hi = self.max_length or "—"
            print(f"Length filter: {lo}–{hi}")

    def _generate_dictionary(
        self,
        output: str = "pass.txt",
        entropy_sort: bool | None = None,
    ) -> None:
        tokens = self._dedup(self.tokens)
        n = len(tokens)
        total = sum(n ** i for i in range(1, self.combination_level + 1))
        print(f"Making combinations from {n} tokens (~{total:,} candidates)...")

        seen: set[str] = set()
        written = 0
        processed = 0

        with open(output, "w") as f:
            for level in range(1, self.combination_level + 1):
                print(f"Starting level {level}...")
                for combo in itertools.product(tokens, repeat=level):
                    processed += 1
                    candidate = "".join(combo)
                    if candidate not in seen and self._passes_length_filter(candidate):
                        seen.add(candidate)
                        f.write(candidate + "\n")
                        written += 1
                    if processed % 50_000 == 0:
                        pct = processed / total * 100
                        sys.stdout.write(f"\r  {processed:,}/{total:,} ({pct:.1f}%) — {written:,} written")
                        sys.stdout.flush()
                sys.stdout.write("\n")
                self._green_print(f"Level {level}: done")

        self._green_print(f"Wrote {written:,} lines to {output}.")

        if entropy_sort is None:
            raw = input("Sort by entropy? Loads all lines into RAM (y/N): ").strip().lower()
            entropy_sort = raw == "y"

        if entropy_sort:
            self._entropy_sort_file(output)

    def _entropy_sort_file(self, path: str) -> None:
        print("Loading file for entropy sort...")
        with open(path) as f:
            lines = [line.rstrip("\n") for line in f]
        print(f"Sorting {len(lines):,} lines...")
        lines.sort(key=self._shannon_entropy)
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")
        self._green_print("Entropy sort done.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _dedup(self, items: list[str]) -> list[str]:
        return sorted(set(items))

    def _green_print(self, text: str) -> None:
        print(f"\033[92m{text} \u2713\033[0m")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="keygen-dictionary",
        description="OSINT-based password dictionary generator for authorized security testing.",
        epilog="Omit all data flags to enter interactive mode.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    data = parser.add_argument_group("target data")
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

    return parser.parse_args()


def _has_data_args(args: argparse.Namespace) -> bool:
    return any([args.name, args.domain, args.address, args.date, args.id, args.additional])


def main() -> None:
    try:
        args = _parse_args()
        maker = DictionaryMaker()

        if _has_data_args(args):
            maker.load_from_args(args)
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
