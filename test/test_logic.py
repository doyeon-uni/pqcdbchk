import pytest
import pandas as pd
import tkinter as tk 
from pqcdbchk.PHREEQC_databasehelper import DatabaseSearcher, EditDatabasePage

def test_search_functionality():
    ss_df = pd.DataFrame({'equation': ['H2O = H+ + OH-', 'NaCl = Na+ + Cl-']})
    sms_df = pd.DataFrame({'species': ['H+', 'Na+']})
    phase_df = pd.DataFrame({'phase_name': ['Calcite', 'Halite']})
    
    searcher = DatabaseSearcher(ss_df, sms_df, phase_df)
    
    result = searcher.search("equation", "H2O")
    assert not result.empty
    assert "H2O" in result.iloc[0]['equation']

    exact_result = searcher.search("phase", "Calcite", exact=True)
    assert len(exact_result) == 1
    
    exact_fail = searcher.search("phase", "Calc", exact=True)
    assert exact_fail.empty

    empty_result = searcher.search("species", "NonExistent")
    assert empty_result.empty

@pytest.fixture(scope="module")
def edit_page():
    root = tk.Tk()
    root.searcher = None
    page = EditDatabasePage(root)
    yield page
    root.destroy()

def test_normalize_equation(edit_page):

    assert edit_page.normalize_equation("H2O=H++OH-") == "H2O = H++OH-"
    assert edit_page.normalize_equation("  Ca+2   =  Ca+2  ") == "Ca+2 = Ca+2"
    assert edit_page.normalize_equation("Ca+2=Ca+2") == "Ca+2 = Ca+2"
    assert edit_page.normalize_equation(None) == ""


def test_find_database_lines(edit_page):
    mock_lines = [
        "SOLUTION_MASTER_SPECIES\n",
        "Ca      Ca+2    0.0     40.08\n",
        "Mg      Mg+2    0.0     24.305\n",
        "PHASES\n",
        "Calcite\n",
        "SOLUTION_SPECIES\n",
        "H2O = H++OH-\n"
    ]
    

    assert edit_page.find_master_species_line(mock_lines, "Mg") == 2
    assert edit_page.find_master_species_line(mock_lines, "Na") == -1
    assert edit_page.find_phase_line(mock_lines, "Calcite") == 4    
    assert edit_page.find_species(mock_lines, "H2O=H++OH-") == 6


def test_insert_into_section(edit_page):
    mock_lines = [
        "SOLUTION_SPECIES\n",
        "H2O = H+ + OH-\n",
        "PHASES\n",
        "Calcite\n"
    ]
    
    new_entry = "Ca+2 = Ca+2\n"
    updated_lines = edit_page.insert_into_section(mock_lines.copy(), "SOLUTION_SPECIES", new_entry)
    assert new_entry in updated_lines
    assert updated_lines.index("PHASES\n") == 3