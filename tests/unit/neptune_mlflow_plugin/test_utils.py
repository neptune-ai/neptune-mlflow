from neptune_mlflow_plugin import create_neptune_tracking_uri
from neptune_mlflow_plugin.impl.utils import (
    decode_config,
    encode_config,
    parse_neptune_kwargs_from_uri,
)


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


def test_parse_uri_warning(recwarn):
    # given
    neptune_uri = create_neptune_tracking_uri(
        project="test_project",
        mode="debug",
        tags=["tag1", "tag2"],
        capture_stdout=True,
        with_id="Test_ID",  # should raise warning
        custom_run_id="Test_custom_id",  # should raise warning
    )

    # when
    neptune_kwargs = parse_neptune_kwargs_from_uri(neptune_uri)

    # then
    assert len(recwarn) == 2
    assert neptune_kwargs == {
        "project": "test_project",
        "mode": "debug",
        "tags": ["tag1", "tag2"],
        "capture_stdout": True,
    }


def test_config_encode_decode():
    # given
    original_config = {
        "val1": True,
        "val2": [1, 2, 4],
        "val3": 56.7,
        "val4": "test",
    }

    # when
    config = decode_config(encode_config(config=original_config))

    assert original_config == config
