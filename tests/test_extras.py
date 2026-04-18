import pytest
from pathlib import Path
from keygen_dictionary import DictionaryMaker, _parse_leet_arg


@pytest.fixture
def maker():
    return DictionaryMaker()


# ── Custom leet map ───────────────────────────────────────────────────────────

class TestCustomLeetMap:
    def test_set_leet_map_overrides_default(self, maker):
        maker.set_leet_map({"a": "@", "e": "3", "s": "$"})
        maker.tokens = ["admin"]
        maker._apply_leet()
        assert "@dmin" in maker.tokens

    def test_custom_map_from_config(self, maker, tmp_path):
        config = tmp_path / "config.yaml"
        config.write_text("name:\n  - 'test'\nleet_map:\n  a: '@'\n  s: '$'\n")
        maker.load_from_config(str(config))
        maker.tokens = ["pass"]
        maker._apply_leet()
        assert "p@$$" in maker.tokens

    def test_parse_leet_arg_valid(self):
        result = _parse_leet_arg("a:4,e:3,s:$")
        assert result == {"a": "4", "e": "3", "s": "$"}

    def test_parse_leet_arg_single(self):
        result = _parse_leet_arg("a:@")
        assert result == {"a": "@"}


# ── Quiet mode ────────────────────────────────────────────────────────────────

class TestQuietMode:
    def test_log_suppressed_when_quiet(self, maker, capsys):
        maker.quiet = True
        maker._log("should not appear")
        captured = capsys.readouterr()
        assert "should not appear" not in captured.out

    def test_log_shown_when_not_quiet(self, maker, capsys):
        maker.quiet = False
        maker._log("should appear")
        captured = capsys.readouterr()
        assert "should appear" in captured.out

    def test_green_print_suppressed_when_quiet(self, maker, capsys):
        maker.quiet = True
        maker._green_print("done")
        captured = capsys.readouterr()
        assert "done" not in captured.out

    def test_final_count_always_printed(self, maker, tmp_path, capsys):
        maker.quiet = True
        maker.full_name = ["Bob"]
        maker._process_input()
        out = str(tmp_path / "out.txt")
        maker._generate_dictionary(output=out, entropy_sort=False)
        captured = capsys.readouterr()
        assert "Wrote" in captured.out


# ── Config save ───────────────────────────────────────────────────────────────

class TestConfigSave:
    def test_save_config_roundtrip(self, maker, tmp_path):
        maker.full_name = ["Jane Doe"]
        maker.domain_name = ["example.com"]
        maker.combination_level = 3
        maker.min_length = 6

        path = str(tmp_path / "saved.yaml")
        maker.save_config(path)

        loader = DictionaryMaker()
        loader.load_from_config(path)
        assert loader.full_name == ["Jane Doe"]
        assert loader.domain_name == ["example.com"]
        assert loader.combination_level == 3
        assert loader.min_length == 6

    def test_save_config_omits_empty_fields(self, maker, tmp_path):
        maker.full_name = ["Alice"]
        path = str(tmp_path / "saved.yaml")
        maker.save_config(path)
        data = Path(path).read_text()
        assert "domain" not in data
        assert "address" not in data

    def test_save_config_file_created(self, maker, tmp_path):
        path = str(tmp_path / "saved.yaml")
        maker.save_config(path)
        assert Path(path).exists()


# ── Case variants ─────────────────────────────────────────────────────────────

class TestCaseVariants:
    def test_upper_variant_added(self, maker):
        maker.full_name = ["john"]
        maker._process_input()
        assert "JOHN" in maker.tokens

    def test_capitalize_variant_added(self, maker):
        maker.full_name = ["john"]
        maker._process_input()
        assert "John" in maker.tokens

    def test_title_variant_added(self, maker):
        maker.full_name = ["john doe"]
        maker._process_input()
        assert "John Doe" in maker.tokens

    def test_no_duplicate_case_variants(self, maker):
        maker.full_name = ["Admin"]
        maker._process_input()
        assert maker.tokens.count("Admin") == 1
