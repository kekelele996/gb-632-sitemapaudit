"""续跑：从已完成的阶段之后接着跑，已采信的字节不再取一次。

续跑只复用同一批次里已入库的采信结果（目录行、收录行、资源摘要），
探测与对账重新执行——这两步不改变输入摘要，所以 run_id 不变，
批次键也不变，重跑不会产生第二行。
"""
from __future__ import annotations

from ... import config, errors
from . import state


def plan(run: dict) -> dict:
    if run is None:
        raise errors.NotFound("批次不存在", code="E_NO_RUN")
    done = state.stages_done(run)
    pending = state.pending_after(done)
    return {"run_id": run["run_id"], "status": run["status"], "done": done,
            "pending": pending, "next": state.next_stage(done),
            "resume_hint": (f"从 {config.STAGE_LABELS[pending[0]]} 继续" if pending
                            else "已完成，无需续跑")}


def can_resume(run: dict) -> bool:
    return bool(state.pending_after(state.stages_done(run)))
