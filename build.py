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
    for line in iter(pipe.readline, ""):
        log_fn(line.rstrip())
    pipe.close()

class VirtualEnvironment:
    def __init__(self, path: Path) -> None:
        self.path = path
        venv = setup_venv(path)
        self.bin_path = venv / ("Scripts" if os.name == "nt" else "bin")
        self.python_executable = self.bin_path / ("python.exe" if os.name == "nt" else "python")
        self.pip_executable = self.bin_path / ("pip.exe" if os.name == "nt" else "pip")
        self.upgrade()

    def run_raw(self, cmd: List[str]) -> None:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        t1 = threading.Thread(target=_stream, args=(p.stdout, logger.info))
        t2 = threading.Thread(target=_stream, args=(p.stderr, logger.info))
        t1.start()
        t2.start()
        p.wait()
        t1.join()
        t2.join()
        if p.returncode != 0:
            raise EnvironmentError(f"Command {cmd} failed with exit code {p.returncode}")

    def run(self, args: List[str]) -> None:
        self.run_raw([str(self.python_executable)] + args)

    def run_module(self, module: str, args: List[str]) -> None:
        self.run_raw([str(self.python_executable), "-m", module] + args)

    def upgrade(self) -> None:
        self.run(["-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])

    def install(self, req: Path) -> None:
        self.run_raw([str(self.pip_executable), "install", "-r", str(req)])

def is_git() -> bool:
    try:
        subprocess.check_output(["git", "--version"])
        return True
    except:
        return False

def get_commit() -> str:
    try:
        c = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return c[:7]
    except:
        return "0000000"

def read_first_line(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return ""

@dataclass
class LicenseMetadata:
    name: str
    owner: str
    year: str

def read_license(path: Path) -> LicenseMetadata:
    if not path.exists():
        return LicenseMetadata("", "", "")
    lines = [l.strip() for l in path.read_text(encoding="utf8").splitlines() if l.strip()]
    header = ""
    for l in lines[:5]:
        if len(l.split()) <= 5:
            header = l
            break
    name = header.replace("License", "").strip()
    c = ""
    for l in lines:
        if "copyright" in l.lower() or "(c)" in l.lower():
            c = l
            break
    y = re.search(r"(19|20)\d{2}", c)
    owner = re.sub(r"(?i)(copyright|\(c\)|©|\d{4})", "", c).strip(" ,") if c else ""
    return LicenseMetadata(name, owner, y.group(0) if y else "")

def commit_to_version(s: str) -> str:
    try:
        n = int(s, 16) % 65535
    except:
        n = 0
    return f"1.0.{n}.0"

def main() -> None:
    if not is_git():
        raise NotInstalled("Git")

    if not Path("assets").exists():
        raise FileNotFoundError("Assets directory missing")

    venv_dir = Path("build")
    dist_dir = Path("dist")
    venv_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)

    venv = VirtualEnvironment(venv_dir)
    venv.install(Path("requirements.txt"))

    commit = get_commit()
    product = Path.cwd().name
    desc = read_first_line(Path("README.md"))
    if commit:
        desc = f"{desc} (Build {commit})"
    lic = read_license(Path("LICENSE"))
    copyright_text = ""
    if lic.name and lic.owner and lic.year:
        copyright_text = f"{lic.name} License (c) {lic.owner} {lic.year}"

    version = commit_to_version(commit)
    tempdir = "{CACHE_DIR}/nuitka"

    args = [
        "--follow-imports",
        "--mode=onefile",
        f"--output-dir={dist_dir}",
        f"--product-name={product}",
        f"--file-description={desc}",
        f"--product-version={version}",
        f"--file-version={version}",
        f"--include-package=scenes",
        f"--onefile-tempdir-spec={tempdir}",
    ]

    assets = Path("assets")
    args.append(f"--include-data-dir={assets.resolve()}=assets")

    icon = assets / "icon.png"
    if os.name == "nt":
        args.append(f"--windows-icon-from-ico={icon}")
    elif "darwin" in sys.platform:
        args.append(f"--macos-app-icon={icon}")
    else:
        args.append(f"--linux-icon={icon}")

    args.append("src/main.py")

    logger.info(f"Starting Nuitka build for {product}...")
    venv.run_module("nuitka", args)
    logger.info(f"Build complete in {dist_dir}")

if __name__ == "__main__":
    main()
