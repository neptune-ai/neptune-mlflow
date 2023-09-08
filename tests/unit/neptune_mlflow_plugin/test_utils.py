from neptune_mlflow_plugin import create_neptune_tracking_uri
from neptune_mlflow_plugin.impl.utils import (
    _parse_tags,
    parse_neptune_kwargs_from_uri,
)


def test_parse_tags():
    tag_strings = [
        "['tag1', 'tag2']",
        "{'tag1', 'tag2', 'tag3'}",
        "single_tag",
    ]

    expected_tags = [
        ["tag1", "tag2"],
        ["tag1", "tag2", "tag3"],
        ["single_tag"],
    ]

    for given, expected in zip(tag_strings, expected_tags):
        assert _parse_tags(given) == expected


def test_parse_uri():
    # given
    neptune_uri = create_neptune_tracking_uri(
        project="test_project",
        mode="debug",
        tags=["tag1", "tag2"],
        capture_stdout=True,
    )

    # when
    neptune_kwargs = parse_neptune_kwargs_from_uri(neptune_uri)

    # then
    assert neptune_kwargs == {
        "project": "test_project",
        "mode": "debug",
        "tags": ["tag1", "tag2"],
        "capture_stdout": True,
    }
