import subprocess
from pathlib import Path

from src.on_chain import poc_lamp


def main():
    script = Path(poc_lamp.__file__).absolute()
    subprocess.run(f"opshin build {script}".split())


if __name__ == "__main__":
    main()
