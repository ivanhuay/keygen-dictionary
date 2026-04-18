import pytest
from pathlib import Path
from keygen_dictionary import DictionaryMaker


@pytest.fixture
def maker():
    return DictionaryMaker()


def _run(maker: DictionaryMaker, tmp_path: Path, **kwargs) -> list[str]:
    """Run full pipeline and return output lines."""
    out = str(tmp_path / "out.txt")
    maker._process_input()
    maker._generate_dictionary(output=out, entropy_sort=kwargs.get("entropy_sort", False))
    return Path(out).read_text().splitlines()


class TestIntegration:
    def test_output_file_non_empty(self, maker, tmp_path):
        maker.full_name = ["John"]
        lines = _run(maker, tmp_path)
        assert len(lines) > 0

    def test_output_contains_name_token(self, maker, tmp_path):
        maker.full_name = ["Alice"]
        lines = _run(maker, tmp_path)
        assert "Alice" in lines

    def test_output_respects_min_length(self, maker, tmp_path):
        maker.full_name = ["Jo"]
        maker.min_length = 5
        lines = _run(maker, tmp_path)
        assert all(len(line) >= 5 for line in lines)

    def test_output_respects_max_length(self, maker, tmp_path):
        maker.full_name = ["Jo"]
        maker.max_length = 4
        lines = _run(maker, tmp_path)
        assert all(len(line) <= 4 for line in lines)

    def test_no_duplicate_lines(self, maker, tmp_path):
        maker.full_name = ["Bob"]
        lines = _run(maker, tmp_path)
        assert len(lines) == len(set(lines))

    def test_entropy_sort_orders_low_first(self, maker, tmp_path):
        maker.full_name = ["test"]
        lines = _run(maker, tmp_path, entropy_sort=True)
        entropies = [DictionaryMaker._shannon_entropy(line) for line in lines]
        assert entropies == sorted(entropies)

    def test_leet_variants_appear_in_output(self, maker, tmp_path):
        maker.full_name = ["admin"]
        lines = _run(maker, tmp_path)
        assert "4dm1n" in lines

    def test_domain_tokens_in_output(self, maker, tmp_path):
        maker.domain_name = ["example.com"]
        lines = _run(maker, tmp_path)
        assert "example" in lines
        assert "com" in lines

    def test_date_tokens_in_output(self, maker, tmp_path):
        maker.important_date = ["01-06-1990"]
        lines = _run(maker, tmp_path)
        assert "1990" in lines
        assert "06" in lines


class TestConfigLoad:
    def test_load_from_yaml(self, maker, tmp_path):
        config = tmp_path / "config.yaml"
        config.write_text(
            "name:\n  - 'Jane Doe'\n"
            "level: 1\n"
            "min_length: 3\n"
        )
        maker.load_from_config(str(config))
        assert maker.full_name == ["Jane Doe"]
        assert maker.combination_level == 1
        assert maker.min_length == 3

    def test_invalid_config_raises(self, maker, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("- just a list\n")
        with pytest.raises(ValueError):
            maker.load_from_config(str(bad))
