from fastapi import APIRouter, Depends

from clases.schemas import TaskCompleteRequest, TaskCreateRequest
from core.security import (
    get_current_user,
    require_admin,
    require_usuario,
)
from services.task_service import (
    complete_user_task,
    create_task_for_user,
    get_task_board_for_supervisor,
    get_task_board_for_user,
    set_task_inactive,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", summary="Crear tarea (supervisor/super_admin)")
def create_task(payload: TaskCreateRequest, current_user=Depends(require_admin)):
    return create_task_for_user(payload, current_user)


@router.get("", summary="Ver tablero de tareas (supervisor/super_admin)")
def list_all_tasks(_=Depends(require_admin)):
    return {"tasks": get_task_board_for_supervisor()}


@router.get("/my", summary="Ver mis tareas (usuario)")
def list_my_tasks(current_user=Depends(get_current_user)):
    return {"tasks": get_task_board_for_user(current_user["id"])}


@router.patch("/{task_id}/complete", summary="Finalizar tarea (usuario)")
def complete_task(task_id: int, payload: TaskCompleteRequest, current_user=Depends(require_usuario)):
    return complete_user_task(task_id, current_user["id"], payload.completion_notes)


@router.patch("/{task_id}/inactive", summary="Inactivar tarea (auditoria)")
def inactivate_task(task_id: int, _=Depends(require_admin)):
    return set_task_inactive(task_id)
