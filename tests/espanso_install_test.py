import contextlib
import io
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from types import SimpleNamespace

from taurcode import espanso_install, prompt_model
from taurcode.cli import main


def _prompt() -> prompt_model.Prompt:
    return prompt_model.Prompt(
        id="test-prompt",
        name="Test Prompt",
        description="A test prompt",
        keyword=":tc-test",
        body="This is a test prompt body.",
    )


def _write_manifest(source_dir: Path, name: str) -> None:
    espanso_dir = source_dir / "espanso"
    espanso_dir.mkdir(parents=True, exist_ok=True)
    (espanso_dir / "_manifest.yml").write_text(
        f"name: {name}\ntitle: Test\ndescription: Test package.\nversion: 0.1.0\n",
        encoding="utf-8",
    )


def _write_prompt_source(source_dir: Path) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "prompt.md").write_text(
        "---\nid: test-prompt\nname: Test Prompt\n"
        'description: A test prompt\nkeyword: ":tc-test"\n---\n\n'
        "This is a test prompt body.\n",
        encoding="utf-8",
    )


class TestResolvePackagesDir(unittest.TestCase):
    def test_rejects_non_darwin_platforms(self) -> None:
        for platform in ("linux", "win32"):
            with self.assertRaises(espanso_install.InstallError):
                espanso_install.resolve_packages_dir(platform, None)

    def test_default_is_expanded_and_absolute(self) -> None:
        resolved = espanso_install.resolve_packages_dir("darwin", None)

        self.assertTrue(resolved.is_absolute())
        self.assertNotIn("~", resolved.parts)

    def test_override_is_expanded(self) -> None:
        resolved = espanso_install.resolve_packages_dir("darwin", "~/custom-packages")

        self.assertTrue(resolved.is_absolute())
        self.assertNotIn("~", resolved.parts)
        self.assertEqual(resolved.name, "custom-packages")

    def test_rejects_relative_override(self) -> None:
        with self.assertRaises(espanso_install.InstallError):
            espanso_install.resolve_packages_dir("darwin", "packages")


class TestResolvePackageName(unittest.TestCase):
    def test_defaults_without_curated_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            name = espanso_install.resolve_package_name(tmpdir)

        self.assertEqual(name, espanso_install.DEFAULT_PACKAGE_NAME)

    def test_derives_from_curated_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir)
            _write_manifest(source_dir, "custompkg")

            name = espanso_install.resolve_package_name(str(source_dir))

        self.assertEqual(name, "custompkg")

    def test_none_source_dir_defaults(self) -> None:
        self.assertEqual(
            espanso_install.resolve_package_name(None),
            espanso_install.DEFAULT_PACKAGE_NAME,
        )


class TestInstallEspanso(unittest.TestCase):
    def test_installs_and_manifest_name_matches_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "prompts"
            _write_manifest(source_dir, "custompkg")
            packages_dir = base / "packages"

            installed = espanso_install.install_espanso(
                [_prompt()], packages_dir, source_dir=str(source_dir)
            )

            self.assertEqual(installed, packages_dir / "custompkg")
            self.assertTrue((installed / "package.yml").is_file())
            manifest_text = (installed / "_manifest.yml").read_text(encoding="utf-8")
            self.assertIn("name: custompkg", manifest_text)
            # No staging directory left behind on success.
            leftovers = list(packages_dir.glob(".taurcode-install-*"))
            self.assertEqual(leftovers, [])

    def test_defaults_to_taurcode_without_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            packages_dir = base / "packages"

            installed = espanso_install.install_espanso(
                [_prompt()], packages_dir, source_dir=None
            )

            self.assertEqual(installed.name, espanso_install.DEFAULT_PACKAGE_NAME)

    def test_rejects_invalid_and_traversal_package_names(self) -> None:
        for bad_name in ("Bad Name", "../victim", "/abs"):
            with tempfile.TemporaryDirectory() as tmpdir:
                base = Path(tmpdir)
                source_dir = base / "prompts"
                _write_manifest(source_dir, bad_name)
                packages_dir = base / "packages"
                packages_dir.mkdir(parents=True)

                with self.assertRaises(espanso_install.InstallError):
                    espanso_install.install_espanso(
                        [_prompt()], packages_dir, source_dir=str(source_dir)
                    )

                # Nothing written anywhere: no traversal escape, no staging dir.
                self.assertEqual(list(packages_dir.iterdir()), [])
                self.assertFalse((base / "victim").exists())

    def test_failed_export_leaves_existing_package_intact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            packages_dir = base / "packages"
            target = packages_dir / "taurcode"
            target.mkdir(parents=True)
            sentinel = target / "package.yml"
            sentinel.write_text("matches: []\n", encoding="utf-8")

            def failing_export(*args, **kwargs):
                raise ValueError("simulated export failure")

            with unittest.mock.patch.object(
                espanso_install.espanso_export, "export_espanso", failing_export
            ):
                with self.assertRaises(ValueError):
                    espanso_install.install_espanso([_prompt()], packages_dir)

            # Export failed before target was touched: install untouched, and no
            # staging directory left behind.
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "matches: []\n")
            self.assertEqual(list(packages_dir.glob(".taurcode-install-*")), [])

    def test_swap_failure_restores_existing_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            packages_dir = base / "packages"
            target = packages_dir / "taurcode"
            target.mkdir(parents=True)
            sentinel = target / "package.yml"
            sentinel.write_text("original\n", encoding="utf-8")

            real_replace = os.replace
            calls = {"n": 0}

            def flaky_replace(src, dst):
                # First replace (target -> backup) succeeds; the second (staged
                # -> target) fails, exercising the rollback path.
                calls["n"] += 1
                if calls["n"] == 2:
                    raise OSError("simulated swap failure")
                return real_replace(src, dst)

            with unittest.mock.patch.object(
                espanso_install.os, "replace", flaky_replace
            ):
                with self.assertRaises(OSError):
                    espanso_install.install_espanso(
                        [_prompt()], packages_dir, source_dir=None
                    )

            # The previous install was restored, not lost to the cleanup.
            self.assertTrue(target.exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "original\n")
            self.assertEqual(list(packages_dir.glob(".taurcode-install-*")), [])


class TestRestartEspanso(unittest.TestCase):
    def test_invokes_runner_when_binary_present(self) -> None:
        calls = []

        def fake_runner(args):
            calls.append(args)
            return SimpleNamespace(returncode=0)

        espanso_install.restart_espanso(
            runner=fake_runner, which=lambda name: "/usr/local/bin/espanso"
        )

        # Invokes the which()-resolved path, not the bare command name.
        self.assertEqual(calls, [["/usr/local/bin/espanso", "restart"]])

    def test_file_not_found_is_wrapped(self) -> None:
        def raising_runner(args):
            raise FileNotFoundError("no such file")

        with self.assertRaises(espanso_install.InstallError):
            espanso_install.restart_espanso(
                runner=raising_runner,
                which=lambda name: "/usr/local/bin/espanso",
            )

    def test_missing_binary_raises(self) -> None:
        with self.assertRaises(espanso_install.InstallError):
            espanso_install.restart_espanso(
                runner=lambda args: SimpleNamespace(returncode=0),
                which=lambda name: None,
            )

    def test_nonzero_exit_raises(self) -> None:
        with self.assertRaises(espanso_install.InstallError):
            espanso_install.restart_espanso(
                runner=lambda args: SimpleNamespace(returncode=1),
                which=lambda name: "/usr/local/bin/espanso",
            )


class TestInstallCli(unittest.TestCase):
    def test_non_darwin_exits_nonzero_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "prompts"
            _write_prompt_source(source_dir)
            packages_dir = base / "packages"

            stderr = io.StringIO()
            with unittest.mock.patch("taurcode.cli.sys.platform", "linux"):
                with contextlib.redirect_stderr(stderr):
                    rc = main(
                        [
                            "install",
                            "espanso",
                            "--prompts",
                            str(source_dir),
                            "--packages-dir",
                            str(packages_dir),
                        ]
                    )

            self.assertEqual(rc, 1)
            self.assertIn("macOS only", stderr.getvalue())
            self.assertFalse(packages_dir.exists())

    def test_installs_and_prints_manual_restart_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_dir = base / "prompts"
            _write_prompt_source(source_dir)
            packages_dir = base / "packages"

            stdout = io.StringIO()
            with unittest.mock.patch("taurcode.cli.sys.platform", "darwin"):
                with contextlib.redirect_stdout(stdout):
                    rc = main(
                        [
                            "install",
                            "espanso",
                            "--prompts",
                            str(source_dir),
                            "--packages-dir",
                            str(packages_dir),
                        ]
                    )

            self.assertEqual(rc, 0)
            self.assertTrue((packages_dir / "taurcode" / "package.yml").is_file())
            self.assertIn("espanso restart", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
