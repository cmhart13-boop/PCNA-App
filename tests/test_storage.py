import storage


def test_project_and_file_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "pcna.db")
    monkeypatch.setattr(storage, "FILES_DIR", tmp_path / "files")

    project_id = storage.save_project(
        "Virtual Request",
        "Ford",
        "Dealer Kit",
        {"Item Number": "1603-02", "Color": "Frost (FRST)"},
    )
    storage.save_upload(project_id, "logo.txt", b"ford")

    projects = storage.list_projects()
    assert len(projects) == 1
    assert projects[0]["customer"] == "Ford"
    assert projects[0]["payload"]["Item Number"] == "1603-02"

    files = storage.list_project_files(project_id)
    assert len(files) == 1
    assert files[0].read_bytes() == b"ford"

    exported = storage.export_projects()
    assert "Dealer Kit" in exported

    storage.delete_project(project_id)
    assert storage.list_projects() == []
