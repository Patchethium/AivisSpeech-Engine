"""UserDictWord のテスト"""

from typing import Literal, TypedDict, get_args

import pytest
from pydantic import ValidationError

from voicevox_engine.tts_pipeline.kana_converter import parse_kana
from voicevox_engine.user_dict.model import UserDictWord


class _UserDictWordInputs(TypedDict):
    surface: str
    priority: int
    part_of_speech: str
    part_of_speech_detail_1: str
    part_of_speech_detail_2: str
    part_of_speech_detail_3: str
    inflectional_type: str
    inflectional_form: str
    stem: list[str]
    yomi: list[str]
    pronunciation: list[str]
    accent_type: list[int]
    accent_associative_rule: str


def generate_model() -> _UserDictWordInputs:
    """テスト用に UserDictWord の要素を生成する。"""
    return {
        "surface": "テスト",
        "priority": 0,
        "part_of_speech": "名詞",
        "part_of_speech_detail_1": "固有名詞",
        "part_of_speech_detail_2": "一般",
        "part_of_speech_detail_3": "*",
        "inflectional_type": "*",
        "inflectional_form": "*",
        "stem": ["*"],
        "yomi": ["テスト"],
        "pronunciation": ["テスト"],
        "accent_type": [0],
        "accent_associative_rule": "*",
    }


def test_valid_word() -> None:
    """generate_model 関数は UserDictWord の要素を生成する。"""
    # Outputs
    args = generate_model()

    # Test
    UserDictWord(**args)


CsvSafeStrFieldName = Literal[
    "part_of_speech",
    "part_of_speech_detail_1",
    "part_of_speech_detail_2",
    "part_of_speech_detail_3",
    "inflectional_type",
    "inflectional_form",
    "accent_associative_rule",
]


@pytest.mark.parametrize(
    "field",
    get_args(CsvSafeStrFieldName),
)
def test_invalid_csv_safe_str(field: CsvSafeStrFieldName) -> None:
    """UserDictWord の文字列 CSV で許可されない文字をエラーとする。"""
    # Inputs
    test_value_newlines = generate_model()
    test_value_newlines[field] = "te\r\nst"
    test_value_null = generate_model()
    test_value_null[field] = "te\x00st"
    test_value_comma = generate_model()
    test_value_comma[field] = "te,st"
    test_value_double_quote = generate_model()
    test_value_double_quote[field] = 'te"st'

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_newlines)
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_null)
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_comma)
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_double_quote)


def test_convert_to_zenkaku() -> None:
    """UserDictWord は surface を全角にする。"""
    # Inputs
    test_value = generate_model()
    test_value["surface"] = "test"
    # Expects
    true_surface = "ｔｅｓｔ"
    # Outputs
    surface = UserDictWord(**test_value).surface

    # Test
    assert surface == true_surface


def test_count_mora() -> None:
    """UserDictWord は mora_count=[] を上書きする。"""
    # Inputs
    test_value = generate_model()
    # Expects
    true_mora_count = 3
    # Outputs
    mora_count = UserDictWord(**test_value).mora_count

    # Test
    assert mora_count == [true_mora_count]


def test_count_mora_x() -> None:
    test_value = generate_model()
    for s in [chr(i) for i in range(12449, 12533)]:
        if s in ["ァ", "ィ", "ゥ", "ェ", "ォ", "ッ", "ャ", "ュ", "ョ", "ヮ"]:
            continue
        for x in "ァィゥェォャュョ":
            expected_count = 0
            test_value["pronunciation"] = [s + x]
            for accent_phrase in parse_kana(
                "".join(test_value["pronunciation"]) + "'",
            ):
                expected_count += len(accent_phrase.moras)
                assert UserDictWord(**test_value).mora_count == [expected_count]


def test_count_mora_xwa() -> None:
    """「ヮ」を含む発音のモーラ数が適切にカウントされる。"""
    # Inputs
    test_value = generate_model()
    test_value["pronunciation"] = ["クヮンセイ"]
    # Expects
    true_mora_count = 0
    for accent_phrase in parse_kana(
        "".join(test_value["pronunciation"]) + "'",
    ):
        true_mora_count += len(accent_phrase.moras)
    # Outputs
    mora_rount = UserDictWord(**test_value).mora_count

    # Test
    assert mora_rount == [true_mora_count]


def test_invalid_pronunciation_not_katakana() -> None:
    """UserDictWord はカタカナでない pronunciation をエラーとする。"""
    # Inputs
    test_value = generate_model()
    test_value["pronunciation"] = ["ぼいぼ"]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value)


def test_invalid_pronunciation_newlines_and_null() -> None:
    """UserDictWord は pronunciation 内の改行や null 文字をエラーとする。"""
    # Inputs
    test_value_newlines = generate_model()
    test_value_newlines["pronunciation"] = ["ボイ\r\nボ"]
    test_value_null = generate_model()
    test_value_null["pronunciation"] = ["ボイ\x00ボ"]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_newlines)
    with pytest.raises(ValidationError):
        UserDictWord(**test_value_null)


def test_invalid_pronunciation_invalid_sutegana() -> None:
    """UserDictWord は無効な pronunciation をエラーとする。"""
    # Inputs
    test_value = generate_model()
    test_value["pronunciation"] = ["アィウェォ"]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value)


def test_invalid_pronunciation_invalid_xwa() -> None:
    """UserDictWord は無効な pronunciation をエラーとする。"""
    # Inputs
    test_value = generate_model()
    test_value["pronunciation"] = ["アヮ"]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value)


def test_count_mora_voiced_sound() -> None:
    """UserDictWord はモーラ数を正しくカウントして上書きする。"""
    # Inputs
    test_value = generate_model()
    test_value["stem"] = ["ボイス", "ボックス"]
    test_value["pronunciation"] = ["ボイス", "ボックス"]
    test_value["yomi"] = ["ボイス", "ボックス"]
    test_value["accent_type"] = [3, 1]
    # Expects
    true_mora_count = [3, 4]
    # Outputs
    mora_count = UserDictWord(**test_value).mora_count

    # Test
    assert mora_count == true_mora_count


def test_word_accent_type_too_big() -> None:
    """UserDictWord はモーラ数を超えた accent_type をエラーとする。"""
    # Inputs
    test_value = generate_model()
    test_value["accent_type"] = [4]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value)


def test_word_accent_type_negative() -> None:
    """UserDictWord は負の accent_type をエラーとする。"""
    # Inputs
    test_value = generate_model()
    test_value["accent_type"] = [-1]

    # Test
    with pytest.raises(ValidationError):
        UserDictWord(**test_value)
