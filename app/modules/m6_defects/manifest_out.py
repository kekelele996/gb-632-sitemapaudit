"""运行清单导出：给复核人一份可复算的 JSON，含每个输入地址的 sha256。

清单内容全部来自已入库的 run，不重新取数，所以导出不会改变任何结论。
"""
from __future__ import annotations

from ... import manifest


def manifest_payload(run: dict) -> dict:
    return manifest.build_manifest(run)


def manifest_json(run: dict) -> str:
    return manifest.manifest_text(run)


def filename(run_id: str) -> str:
    return f"manifest-{run_id}.json"
