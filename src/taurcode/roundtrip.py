import dataclasses
from pathlib import Path

from taurcode import semantic_normalize


@dataclasses.dataclass(frozen=True)
class RoundtripComparison:
    prompt_count: int
    metadata_asset_count: int
    differences: tuple[semantic_normalize.SemanticDifference, ...]

    def passed(self) -> bool:
        return not self.differences


def compare_espanso_roundtrip(
    input_path: str | Path, prompts_path: str | Path
) -> RoundtripComparison:
    expected = semantic_normalize.normalize_canonical_prompts(prompts_path)
    actual = semantic_normalize.normalize_espanso_package(input_path)
    differences = semantic_normalize.compare_packages(
        expected,
        actual,
        mode=semantic_normalize.ESPANSO_SEMANTIC_MODE,
    )
    return RoundtripComparison(
        prompt_count=len(expected.prompts),
        metadata_asset_count=_expected_metadata_asset_count(expected),
        differences=tuple(differences),
    )


def format_roundtrip_summary(comparison: RoundtripComparison) -> str:
    if comparison.passed():
        lines = [
            "Roundtrip semantic comparison passed.",
            "",
            f"Prompts compared: {comparison.prompt_count}",
            f"Metadata assets compared: {comparison.metadata_asset_count}",
            "Differences: 0",
        ]
        return "\n".join(lines)

    lines = [
        "Roundtrip semantic comparison failed.",
        "",
        f"Prompts compared: {comparison.prompt_count}",
        f"Metadata assets compared: {comparison.metadata_asset_count}",
        f"Differences: {len(comparison.differences)}",
        "",
        "Differences:",
    ]
    for difference in comparison.differences:
        lines.append(f"- {difference.path}: {difference.message}")
    return "\n".join(lines)


def _expected_metadata_asset_count(
    package: semantic_normalize.NormalizedPackage,
) -> int:
    values = (package.manifest, package.readme, package.license_text)
    return sum(value is not None for value in values)
