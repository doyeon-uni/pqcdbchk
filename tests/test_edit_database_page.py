import tkinter as tk

import pytest

from pqcdbchk import PHREEQC_databasehelper as helper
from pqcdbchk.PHREEQC_databasehelper import EditDatabasePage


@pytest.fixture
def edit_page():
    root = tk.Tk()
    root.searcher = None
    page = EditDatabasePage(root)
    yield page
    root.destroy()


@pytest.fixture(autouse=True)
def stub_messageboxes(monkeypatch):
    monkeypatch.setattr(helper.messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(helper.messagebox, "showwarning", lambda *a, **k: None)
    monkeypatch.setattr(helper.messagebox, "askyesno", lambda *a, **k: True)


def _set(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, value)


def test_add_species_appends_new_species(edit_page, tmp_path):
    db_path = tmp_path / "db.dat"
    db_path.write_text("SOLUTION_SPECIES\nH2O = H+ + OH-\n\nPHASES\n")
    new_path = tmp_path / "out.dat"

    _set(edit_page.entry_db, str(db_path))
    _set(edit_page.entry_new, str(new_path))
    _set(edit_page.entry_eq, "Na+ = Na+")
    _set(edit_page.entry_logk, "0.0")
    _set(edit_page.entry_dh, "0.0")

    edit_page.add_species()

    content = new_path.read_text()
    assert "Na+ = Na+" in content
    assert "log_k 0.0" in content


def test_add_species_edits_existing_duplicate(edit_page, tmp_path):
    db_path = tmp_path / "db.dat"
    db_path.write_text("SOLUTION_SPECIES\nH2O = H+ + OH-\n    log_k 14.0\n\nPHASES\n")
    new_path = tmp_path / "out.dat"

    _set(edit_page.entry_db, str(db_path))
    _set(edit_page.entry_new, str(new_path))
    _set(edit_page.entry_eq, "H2O=H++OH-")
    _set(edit_page.entry_logk, "-14.0")
    _set(edit_page.entry_dh, "13.4")

    edit_page.add_species()

    content = new_path.read_text()
    assert content.count("H2O = H+ + OH-") == 1
    assert "log_k -14.0" in content


def test_add_master_species_appends_new_element(edit_page, tmp_path):
    db_path = tmp_path / "db.dat"
    db_path.write_text("SOLUTION_MASTER_SPECIES\nCa      Ca+2    0.0     40.08\n\nPHASES\n")
    new_path = tmp_path / "out.dat"

    _set(edit_page.entry_db, str(db_path))
    _set(edit_page.entry_new, str(new_path))
    _set(edit_page.entry_sms_element, "Mg")
    _set(edit_page.entry_sms_species, "Mg+2")
    _set(edit_page.entry_sms_alk, "0.0")
    _set(edit_page.entry_sms_gfw, "24.305")

    edit_page.add_master_species()

    content = new_path.read_text()
    assert "Mg    Mg+2    0.0    24.305" in content


def test_add_phase_appends_new_phase(edit_page, tmp_path):
    db_path = tmp_path / "db.dat"
    db_path.write_text("PHASES\nCalcite\n    CaCO3 = Ca+2 + CO3-2\n    log_k -8.48\n\nEXCHANGE\n")
    new_path = tmp_path / "out.dat"

    _set(edit_page.entry_db, str(db_path))
    _set(edit_page.entry_new, str(new_path))
    _set(edit_page.entry_phase_name, "Fluorite")
    _set(edit_page.entry_phase_eq, "CaF2 = Ca+2 + 2F-")
    _set(edit_page.entry_phase_logk, "-10.6")
    _set(edit_page.entry_phase_dh, "0.0")

    edit_page.add_phase()

    content = new_path.read_text()
    assert "Fluorite" in content
    assert "CaF2 = Ca+2 + 2F-" in content


def test_add_species_warns_on_missing_input(edit_page, monkeypatch, tmp_path):
    warnings = []
    monkeypatch.setattr(
        helper.messagebox, "showwarning", lambda *a, **k: warnings.append(a)
    )

    edit_page.add_species()

    assert warnings
