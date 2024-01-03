import sys
from pathlib import Path

temp_docs_dir = Path(sys.argv[1])

with open(temp_docs_dir / "index.md", "w") as md_f:
    md_f.writelines([
        "# Hello",
        "Welcome to project 1's docs!"
    ])

with open(temp_docs_dir / "about.md", "w") as md_f:
    md_f.writelines([
        "# About",
        "This is the about page."
    ])