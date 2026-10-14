"""Run current user-flow and personal-storage acceptance / 运行当前流程与个人存储验收。"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    for name in ["reading_guide_browser_check.py", "personal_browser_check.py"]:
        runpy.run_path(str(Path(__file__).with_name(name)), run_name="__main__")
