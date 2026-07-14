from pqcdbchk.build_database.utils import phreeqc_database_list


def test_phreeqc_database_list_returns_all_dat_files(tmp_path):
    (tmp_path / "a.dat").touch()
    (tmp_path / "b.dat").touch()
    (tmp_path / "notes.txt").touch()

    result = phreeqc_database_list(tmp_path)

    assert sorted(result) == sorted(
        [str(tmp_path / "a.dat"), str(tmp_path / "b.dat")]
    )


def test_phreeqc_database_list_excludes_ignored_files(tmp_path):
    (tmp_path / "a.dat").touch()
    (tmp_path / "b.dat").touch()

    result = phreeqc_database_list(tmp_path, ignore=["b.dat"])

    assert result == [str(tmp_path / "a.dat")]
