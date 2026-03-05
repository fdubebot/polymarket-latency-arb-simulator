import json

from latarb.config import load_app_config


def test_config_file_env_and_overrides_precedence(tmp_path, monkeypatch) -> None:
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(
        json.dumps(
            {
                "simulation": {"steps": 100, "seed": 2},
                "risk": {"max_abs_inventory": 55.0},
                "output": {"run_name": "from-file"},
            }
        )
    )
    monkeypatch.setenv("LATARB_SIM_STEPS", "150")
    monkeypatch.setenv("LATARB_RISK_MAX_ABS_INVENTORY", "65")

    cfg = load_app_config(
        config_path=str(cfg_path),
        overrides={"simulation": {"steps": 200}, "output": {"run_name": "from-cli"}},
    )

    assert cfg.simulation.steps == 200
    assert cfg.simulation.seed == 2
    assert cfg.risk.max_abs_inventory == 65
    assert cfg.output.run_name == "from-cli"
