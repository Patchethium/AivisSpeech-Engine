"""プリセット機能を提供する API Router"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from voicevox_engine.preset.model import Preset
from voicevox_engine.preset.preset_manager import (
    PresetInputError,
    PresetInternalError,
    PresetManager,
)

from ..dependencies import VerifyMutabilityAllowed


def generate_preset_router(
    preset_manager: PresetManager, verify_mutability: VerifyMutabilityAllowed
) -> APIRouter:
    """プリセット API Router を生成する"""
    router = APIRouter(tags=["プリセット"])

    @router.get(
        "/presets",
        summary="エンジンが保持しているプリセットの設定を取得する",
        response_description="プリセットのリスト",
    )
    def get_presets() -> list[Preset]:
        """
        エンジンが保持しているプリセットの設定を返します。
        """
        try:
            presets = preset_manager.load_presets()
        except PresetInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except PresetInternalError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        return presets

    @router.post(
        "/add_preset",
        summary="新しいプリセットを追加する",
        response_description="追加したプリセットのプリセットID",
        dependencies=[Depends(verify_mutability)],
    )
    def add_preset(
        preset: Annotated[
            Preset,
            Body(
                description="新しいプリセット。プリセットIDが既存のものと重複している場合は、新規のプリセットIDが採番されます。"
            ),
        ],
    ) -> int:
        """
        新しいプリセットを追加します。
        """
        try:
            id = preset_manager.add_preset(preset)
        except PresetInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except PresetInternalError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        return id

    @router.post(
        "/update_preset",
        summary="既存のプリセットを更新する",
        response_description="更新したプリセットのプリセットID",
        dependencies=[Depends(verify_mutability)],
    )
    def update_preset(
        preset: Annotated[
            Preset,
            Body(
                description="更新するプリセット。プリセットIDが更新対象と一致している必要があります。"
            ),
        ],
    ) -> int:
        """
        既存のプリセットを更新します。
        """
        try:
            id = preset_manager.update_preset(preset)
        except PresetInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except PresetInternalError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        return id

    @router.post(
        "/delete_preset",
        summary="既存のプリセットを削除する",
        status_code=204,
        dependencies=[Depends(verify_mutability)],
    )
    def delete_preset(
        id: Annotated[int, Query(description="削除するプリセットのプリセットID")],
    ) -> None:
        """
        既存のプリセットを削除します。
        """
        try:
            preset_manager.delete_preset(id)
        except PresetInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except PresetInternalError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return router
