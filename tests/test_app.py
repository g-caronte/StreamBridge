import pytest
from streambridge.app import app


@pytest.mark.parametrize(
    "initial, final",
    [
        ({}, {"anyname": "anyvalue"}),
        ({"anyname": "anyvalue"}, {}),
        ({"anyname": "avalue"}, {"anyname": "anyvalue", "aa": "11"}),
    ],
)
def test_config_overide(app_client, initial, final):
    app.restream_config.clear()
    app.restream_config.update(initial)

    assert app_client.get("/config").json == initial
    assert app_client.post("/config", json=final).json == final
    assert app_client.get("/config").json == final


@pytest.mark.parametrize(
    "initial, update, final",
    [
        ({}, {"anyname": "anyvalue"}, {"anyname": "anyvalue"}),
        ({"anyname": "anyvalue"}, {}, {"anyname": "anyvalue"}),
        ({"anyname": "avalue"}, {"anyname": "anyvalue", "aa": "11"}, {"anyname": "anyvalue", "aa": "11"}),
    ],
)
def test_config_update(app_client, initial, update, final):
    app.restream_config.clear()
    app.restream_config.update(initial)

    assert app_client.get("/config").json == initial
    assert app_client.put("/config", json=update).json == final
    assert app_client.get("/config").json == final
