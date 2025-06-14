"""/singer_info API のテスト。"""

from fastapi.testclient import TestClient
from syrupy.assertion import SnapshotAssertion

from test.utility import hash_long_string


def test_get_singer_info_200(
    client: TestClient, snapshot_json: SnapshotAssertion
) -> None:
    response = client.get(
        "/singer_info", params={"speaker_uuid": "b1a81618-b27b-40d2-b0ea-27a9ad408c4b"}
    )
    # AivisSpeech Engine では未実装 (501 Not Implemented を返す)
    assert response.status_code == 501
    return
    assert response.status_code == 200
    assert snapshot_json == hash_long_string(response.json())


def test_get_singer_info_with_url_200(
    client: TestClient, snapshot_json: SnapshotAssertion
) -> None:
    response = client.get(
        "/singer_info",
        params={
            "speaker_uuid": "b1a81618-b27b-40d2-b0ea-27a9ad408c4b",
            "resource_format": "url",
        },
    )
    # AivisSpeech Engine では未実装 (501 Not Implemented を返す)
    assert response.status_code == 501
    return
    assert response.status_code == 200
    assert snapshot_json == hash_long_string(response.json())
