from typing import IO, Any, Callable, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import subprocess
import threading
import logging
import sys
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotInstalled(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"{name} not installed or not found in PATH.")


def setup_venv(target_dir: Path) -> Path:
    subprocess.run(["python", "-m", "venv", target_dir / ".venv"], check=True)
    return target_dir / ".venv"


def _stream(pipe: IO[str], log_fn: Callable[[str], Any]) -> None:
    for line in iter(pipe.readline, ''):
        log_fn(line.rstrip())
    pipe.close()


class VirtualEnvironment:
    def __init__(self, path: Path) -> None:
        self.path = path
        venv = setup_venv(path)
        self.bin_path = venv / "Scripts" if os.name == "nt" else venv / "bin"
        self.lib_path = venv / "Libs" if os.name == "nt" else venv / "lib"
        self.python_executable = self.bin_path / ("python.exe" if os.name == "nt" else "python")
        self.pip_executable = self.bin_path / ("pip.exe" if os.name == "nt" else "pip")
        self.upgrade_to_newest()

    def run_as(self, runner: Path, target: Optional[Path | str] = None, args: Optional[List[str]] = None) -> None:
        command = [str(runner)]
        if target:
            command.append(str(target))
        if args:
            command.extend(args)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        t_out = threading.Thread(target=_stream, args=(process.stdout, logger.info))
        t_err = threading.Thread(target=_stream, args=(process.stderr, logger.info))
        t_out.start()
        t_err.start()

        process.wait()
        t_out.join()
        t_err.join()

        if process.returncode != 0:
            raise EnvironmentError(
                f"Command {command} failed with return code {process.returncode}"
            )

    def run(self, target: Optional[Path | str] = None, args: Optional[List[str]] = None) -> None:
        self.run_as(self.python_executable, target, args)

    def install_package(self, package: str) -> None:
        subprocess.run([str(self.pip_executable), "install", package], check=True)

    def is_package_installed(self, package: str) -> bool:
        try:
            subprocess.check_output([str(self.pip_executable), "show", package])
            return True
        except subprocess.CalledProcessError:
            return False

    def install_from_requirements(self, requirements_path: Path) -> None:
        subprocess.run(
            [str(self.pip_executable), "install", "-r", str(requirements_path)],
            check=True,
            text=True
        )

    def upgrade_to_newest(self) -> None:
        # python -m pip install --upgrade ...
        self.run("-m", ["pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
        version = subprocess.check_output(
            [str(self.python_executable), "--version"], text=True
        ).strip()
        logger.info(f"Virtual environment Python version: {version}")


def is_git_installed() -> bool:
    try:
        subprocess.check_output(["git", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_patchelf_installed() -> bool:
    try:
        subprocess.check_output(["patchelf", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_github_commit_id() -> Optional[str]:
    try:
        commit_id = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return commit_id[:7]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def setup_build_directory(name: str, path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def check_required_packages(purpose: str, packages: Set[str]) -> None:
    missing = {
        pkg
        for pkg in packages
        if subprocess.run(["pip", "show", pkg], capture_output=True).returncode != 0
    }
    if missing:
        raise NotInstalled(", ".join(missing))


def require_packages_from_file(purpose: str, requirements_path: Path) -> None:
    packages = {
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    check_required_packages(purpose, packages)


def read_first_non_title_line(readme: Path) -> str:
    if not readme.exists():
        return ""
    lines = [l.strip() for l in readme.read_text(encoding="utf-8").splitlines()]
    for line in lines:
        if line and not line.startswith("#"):
            return line
    return ""


@dataclass
class LicenseMetadata:
    name: str
    owner: str
    year: str


def read_license_metadata(license_path: Path) -> LicenseMetadata:
    if not license_path.exists():
        return LicenseMetadata("", "", "")
    lines = [
        line.strip()
        for line in license_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    header = ""
    for line in lines[:5]:
        if len(line.split()) <= 5:
            header = line
            break

    license_name = header.replace("License", "").strip() if header else ""

    copyright_line = ""
    for line in lines:
        if "(c)" in line.lower() or "copyright" in line.lower():
            copyright_line = line
            break

    year_match = re.search(r"(19|20)\d{2}", copyright_line)
    owner_match = re.sub(r"(?i)(copyright|\(c\)|©|\d{4})", "", copyright_line).strip()

    year = year_match.group(0) if year_match else ""
    owner = owner_match.strip(" ,") if owner_match else ""

    return LicenseMetadata(license_name, owner, year)


def main() -> None:
    if not is_git_installed():
        raise NotInstalled("Git")

    if not Path("assets").exists():
        raise FileNotFoundError("Assets directory not found.")

    require_packages_from_file("development", Path("requirements.txt"))

    commit_id = get_github_commit_id()
    if commit_id:
        logger.info(f"Building from commit {commit_id}")
    else:
        logger.warning("No commit ID found, build will not be tagged.")

    build_dir = setup_build_directory("build", Path("build"))
    dist_dir = setup_build_directory("dist", Path("dist"))
    venv = VirtualEnvironment(build_dir)

    venv.install_from_requirements(Path("requirements.txt"))

    license = read_license_metadata(Path("LICENSE"))

    product_name = Path.cwd().name.strip()
    description_text = read_first_non_title_line(Path("README.md"))
    full_description = f"{description_text} (Build {commit_id})" if commit_id else description_text
    copyright_text = (
        f"{license.name} License (c) {license.owner} {license.year}"
        if license.name and license.owner and license.year
        else ""
    )

    onefile_tempdir = Path.home() / ".cache" / "nuitka"

    build_args = [
        "--follow-imports",
        f"--output-dir={dist_dir}",
        f"--product-name={product_name}",
        f"--file-description={full_description}",
        f"--copyright={copyright_text}",
        "--include-package=scenes",
        "--mode=onefile",
        f"--onefile-tempdir-spec={onefile_tempdir}",
    ]

    assets_dir = Path("assets")
    if assets_dir.exists():
        build_args.append(f"--include-data-dir={str(assets_dir.resolve())}=assets")
    else:
        logger.warning("No assets directory found at ./assets")

    icon = Path("assets/icon.png")
    if icon.exists():
        if os.name == "nt":
            build_args.append(f"--windows-icon-from-ico={icon}")
        elif "darwin" in sys.platform:
            build_args.append(f"--macos-app-icon={icon}")
        else:
            build_args.append(f"--linux-icon={icon}")
    else:
        logger.warning("No icon file found at assets/icon.png")

    build_args.append("src/main.py")

    if os.name == "nt":
        nuitka_executable = venv.bin_path / "nuitka.bat"
    else:
        nuitka_executable = venv.bin_path / "nuitka"
    logger.info(
        f"Building {product_name} from commit {commit_id} with an {license.name} license. This may take a while..."
    )
    venv.run_as(nuitka_executable, None, build_args)

    logger.info(f"Build completed. Output located in {dist_dir}")


if __name__ == "__main__":
    main()
