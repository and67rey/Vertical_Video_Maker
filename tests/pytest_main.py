from main import main

def test_main_entry(monkeypatch):
    called = {"logging": False, "args": False, "run": False}

    def fake_setup_logging():
        called["logging"] = True

    def fake_parse_args():
        called["args"] = True
        return "fake_args"

    def fake_run_vvm(args):
        called["run"] = args == "fake_args"

    monkeypatch.setattr("main.setup_logging", fake_setup_logging)
    monkeypatch.setattr("main.parse_args", fake_parse_args)
    monkeypatch.setattr("main.run_vvm", fake_run_vvm)

    main()
    assert all(called.values())
