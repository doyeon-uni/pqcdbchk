from pqcdbchk.database_editor import (
    find_master_species_line,
    find_phase_line,
    find_species,
    insert_into_section,
    normalize_equation,
)


# DatabaseSearcher behavior is covered by tests/test_database_searcher.py


def test_normalize_equation():
    assert normalize_equation("H2O=H++OH-") == "H2O = H++OH-"
    assert normalize_equation("  Ca+2   =  Ca+2  ") == "Ca+2 = Ca+2"
    assert normalize_equation("Ca+2=Ca+2") == "Ca+2 = Ca+2"
    assert normalize_equation(None) == ""


def test_find_database_lines():
    mock_lines = [
        "SOLUTION_MASTER_SPECIES\n",
        "Ca      Ca+2    0.0     40.08\n",
        "Mg      Mg+2    0.0     24.305\n",
        "PHASES\n",
        "Calcite\n",
        "SOLUTION_SPECIES\n",
        "H2O = H++OH-\n",
    ]

    assert find_master_species_line(mock_lines, "Mg") == 2
    assert find_master_species_line(mock_lines, "Na") == -1
    assert find_phase_line(mock_lines, "Calcite") == 4
    assert find_species(mock_lines, "H2O=H++OH-") == 6


def test_insert_into_section():
    mock_lines = ["SOLUTION_SPECIES\n", "H2O = H+ + OH-\n", "PHASES\n", "Calcite\n"]

    new_entry = "Ca+2 = Ca+2\n"
    updated_lines = insert_into_section(
        mock_lines.copy(), "SOLUTION_SPECIES", new_entry
    )
    assert new_entry in updated_lines
    assert updated_lines.index("PHASES\n") == 3
