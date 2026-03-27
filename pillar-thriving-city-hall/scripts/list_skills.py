#!/usr/bin/env python3
"""
List discovered Hackbot skills by scanning skills/**/SKILL.md.

Outputs one skill name per line, sorted alphabetically.
"""
from pathlib import Path

def discover_skills(base: Path) -> list[str]:
    skills_dir = base / "skills"
    names = []
    if not skills_dir.exists():
        return names
    for p in sorted(skills_dir.iterdir()):
        if not p.is_dir():
            continue
        if (p / "SKILL.md").exists():
            names.append(p.name)
    return names

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for name in discover_skills(root):
        print(name)

