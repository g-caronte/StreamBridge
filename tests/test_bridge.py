from unittest import mock

from streamlink.plugin import Plugin

from streambridge import bridge


@mock.patch("streamlink.session.Streamlink.resolve_url")
def test_cached_resolution(resolve_url_mock: mock.MagicMock):
    plugin_class = mock.Mock()
    resolve_url_mock.return_value = "aPlugin", plugin_class, "the url"

    bridge.resolve("http://sameurl.com")
    bridge.resolve("http://sameurl.com")

    resolve_url_mock.assert_called_once()


@mock.patch("streamlink.session.Streamlink.resolve_url")
def test_plugin_parameters(resolve_url_mock: mock.MagicMock):
    plugin_class = mock.Mock(Plugin)
    resolve_url_mock.return_value = "aPlugin", plugin_class, "http://anotherurl.com"

    bridge.resolve(
        "http://anotherurl.com",
        {
            "generic-param": "anyvalue",
            "aPlugin-param": "anyvalue2",
            "anotherPlugin-param": "anyvalue3",
        },
    )

    plugin_class.assert_any_call(mock.ANY, "http://anotherurl.com", {"param": "anyvalue2"})
