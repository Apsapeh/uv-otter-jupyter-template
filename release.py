import shutil
import os
import sys
import zipfile
import subprocess
from pathlib import Path

############### Настройки ###################
DEFAULT_NOTEBOOK = "Task.ipynb"
DEFAULT_OUTPUT = "Task.zip"
DEFAULT_README = "RELEASE_README.md"
DEFAULT_DIST_DIR = Path(".tmp-dist")
#############################################


def main():
    if DEFAULT_DIST_DIR.exists():
        shutil.rmtree(DEFAULT_DIST_DIR);
    DEFAULT_DIST_DIR.mkdir();
    
    print("Генерируем requirements.txt...")
    req_result = subprocess.run(
        ["uv", "export", "--no-dev", "--no-hashes", "--format", "requirements-txt"],
        capture_output=True, text=True
    )
    if req_result.returncode != 0:
        error("")
    else:
        requirements_txt = req_result.stdout
        
    print("Компилируем ноутбук...")
    req_result = subprocess.run(
        ["uv", "run", "--with", "otter-grader", "otter", "assign", DEFAULT_NOTEBOOK, str(DEFAULT_DIST_DIR)]
    )
    if req_result.returncode != 0:
        error("")
        
    student_nb = try_get_file(DEFAULT_DIST_DIR / "student" / DEFAULT_NOTEBOOK, "Скомпилированный ноутбук не найден")
    pyproject = try_get_file(Path("pyproject.toml"), "UV pyproject.toml не найден")
    readme = try_get_file(Path(DEFAULT_README), "Релизный README не найден")
        
    print(f"Собираем в один архив ({DEFAULT_OUTPUT})")
    with zipfile.ZipFile(DEFAULT_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(student_nb, DEFAULT_NOTEBOOK)
        zf.write(pyproject, "pyproject.toml")
        zf.write(readme, "README.MD")
        zf.writestr("requirements.txt", requirements_txt)
        
        
def try_get_file(file: Path, err_msg: str) -> Path:
    if not file.exists():
        error(err_msg)
    return file
    


def error(msg):
    print("ОШИБКА!!! " + msg, file=sys.stderr)
    sys.exit(1);

if __name__ == "__main__":
    main()
