"""Pure, framework-independent logic for editing PHREEQC database files.

These functions operate on plain lists of lines / strings and do not
depend on Tkinter, so they can be unit tested without a display or a
running GUI.
"""
import os
import re


def normalize_equation(s: str) -> str:
    """Add single spaces around '=' and collapse repeated whitespace."""
    if s is None:
        return ""
    s = s.strip()
    s = re.sub(r'\s*=\s*', ' = ', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def find_species(lines: list, species_eq: str) -> int:
    """Return the index of a matching SOLUTION_SPECIES equation, or -1."""
    target = normalize_equation(species_eq)
    if not target:
        return -1

    for i, line in enumerate(lines):
        if normalize_equation(line) == target:
            return i
    return -1


def find_master_species_line(lines: list, element_name: str) -> int:
    """Return the index of a SOLUTION_MASTER_SPECIES element line, or -1."""
    pattern = re.compile(rf'^\s*{re.escape(element_name)}\s+')
    for i, line in enumerate(lines):
        if pattern.match(line):
            return i
    return -1


def find_phase_line(lines: list, phase_name: str) -> int:
    """Return the index of a PHASES phase name line, or -1."""
    pattern = re.compile(rf'^\s*{re.escape(phase_name)}\s*$')
    for i, line in enumerate(lines):
        if pattern.match(line):
            return i
    return -1


def insert_into_section(lines: list, section_name: str, new_entry: str) -> list:
    """Insert new_entry at the end of the given section, in place."""
    start = None
    pattern = re.compile(rf'^\s*{re.escape(section_name)}\s*$', re.IGNORECASE)
    for i, line in enumerate(lines):
        if pattern.match(line):
            start = i
            break
    if start is None:
        raise ValueError(f"Section {section_name} not found.")
    end = None
    for i in range(start + 1, len(lines)):
        s = lines[i].strip()
        if not s:
            continue
        if re.match(r'^[A-Z][A-Z _]*[A-Z]$', s):
            end = i
            break
    if end is None:
        end = len(lines)
    new_lines = new_entry.splitlines(keepends=True)
    for j, nl in enumerate(new_lines):
        if not nl.endswith('\n'):
            new_lines[j] = nl + '\n'
    lines[end:end] = new_lines
    return lines


def load_database(path: str) -> list:
    """Load a database file's lines, or an empty list if it doesn't exist."""
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return f.readlines()


def save_database(lines: list, path: str) -> None:
    """Write database lines to path."""
    with open(path, 'w') as f:
        f.writelines(lines)
