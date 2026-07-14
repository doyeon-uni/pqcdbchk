import io

from pqcdbchk.build_database.clean_tables import compile_phase_table
from pqcdbchk.build_database.write_dataframes import write_phase


PHASES_A = """PHASES
Calcite
 CaCO3 = CO3-2 + Ca+2
 -log_k -8.48
 -delta_h -2.297 kcal
 -Vm 36.9
Steam
 H2O = H2O
 -log_k 1.506
 -T_c  647.3; -P_c   217.60; -Omega 0.344
EXCHANGE
"""

PHASES_B = """PHASES
Calcite
 CaCO3 = CO3-2 + Ca+2
 -log_k -8.48
 -delta_h -2.297 kcal
 -Vm 36.9
Fluorite
 CaF2 = Ca+2 + 2 F-
 -log_k -10.6
EXCHANGE
"""


def test_compile_phase_table_parses_and_cleans_a_single_database(tmp_path):
    db_path = tmp_path / "phases_a.dat"
    db_path.write_text(PHASES_A)

    result = compile_phase_table([str(db_path)])

    assert sorted(result["phase_name"]) == ["Calcite", "Steam"]

    calcite = result[result["phase_name"] == "Calcite"].iloc[0]
    assert calcite["dissolution_reaction"] == "CaCO3 = CO3-2 + Ca+2"
    assert calcite["log_k"] == -8.48
    assert calcite["v_m"] == (36.9,)
    assert calcite["t_c"] is None
    assert calcite["p_c"] is None
    assert calcite["omega"] is None

    steam = result[result["phase_name"] == "Steam"].iloc[0]
    assert steam["dissolution_reaction"] == "H2O = H2O"
    assert steam["log_k"] == 1.506
    assert steam["t_c"] == 647.3
    assert steam["p_c"] == 217.6
    assert steam["omega"] == 0.344


def test_compile_phase_table_merges_and_deduplicates_across_databases(tmp_path):
    db_path_a = tmp_path / "phases_a.dat"
    db_path_a.write_text(PHASES_A)
    db_path_b = tmp_path / "phases_b.dat"
    db_path_b.write_text(PHASES_B)

    result = compile_phase_table([str(db_path_a), str(db_path_b)])

    # Calcite appears identically in both databases and should be deduplicated
    assert sorted(result["phase_name"]) == ["Calcite", "Fluorite", "Steam"]


def test_write_phase_writes_phreeqc_formatted_block(tmp_path):
    db_path = tmp_path / "phases_a.dat"
    db_path.write_text(PHASES_A)

    result = compile_phase_table([str(db_path)])
    row = result.set_index("phase_name", drop=False).loc["Calcite"]

    with io.StringIO() as buffer:
        write_phase(row, buffer)
        content = buffer.getvalue()

    assert content.startswith("Calcite\n")
    assert "CaCO3 = CO3-2 + Ca+2\n" in content
    assert "\tlog_k\t-8.48\n" in content
    assert "\t# source\t" in content
