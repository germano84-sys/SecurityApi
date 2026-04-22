from fastapi import APIRouter, Depends

from secureapi.clases.schemas import (
    MilestoneIssueCreateRequest,
    MilestoneIssueListResponse,
    MilestoneIssueResponse,
    TaskCreateRequest,
    TaskCreatedResponse,
    TaskInactiveResponse,
    TaskListResponse,
    TaskStatusUpdateRequest,
    TaskStatusUpdatedResponse,
)
from secureapi.core.security import (
    get_current_user,
    require_supervisor_or_admin,
    require_usuario_comun,
)
from secureapi.services.task_service import (
    create_milestone_issue_entry,
    create_task_for_user,
    get_milestone_issue_catalog,
    get_task_board_for_supervisor,
    get_task_board_for_user,
    set_task_inactive,
    update_user_task_status,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", summary="Crear tarea (supervisor/admin)", response_model=TaskCreatedResponse)
def create_task(payload: TaskCreateRequest, current_user=Depends(require_supervisor_or_admin)):
    return create_task_for_user(payload, current_user)


@router.get("", summary="Ver tablero de tareas (supervisor/admin)", response_model=TaskListResponse)
def list_all_tasks(
    status: str | None = None,
    assigned_to_username: str | None = None,
    _=Depends(require_supervisor_or_admin),
):
    return {
        "tasks": get_task_board_for_supervisor(
            status=status,
            assigned_to_username=assigned_to_username,
        )
    }


@router.get("/my", summary="Ver mis tareas (usuario)", response_model=TaskListResponse)
def list_my_tasks(current_user=Depends(get_current_user)):
    return {"tasks": get_task_board_for_user(current_user["id"])}


@router.patch("/{task_id}/status", summary="Actualizar estado de tarea (usuario_comun)", response_model=TaskStatusUpdatedResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    current_user=Depends(require_usuario_comun),
):
    return update_user_task_status(task_id, current_user["id"], payload.status, payload.notes)


@router.get("/milestones", summary="Catalogo de milestone issues", response_model=MilestoneIssueListResponse)
def milestone_catalog(_=Depends(require_supervisor_or_admin)):
    return {"items": get_milestone_issue_catalog()}


@router.post("/milestones", summary="Crear milestone issue en catalogo", response_model=MilestoneIssueResponse)
def create_milestone(payload: MilestoneIssueCreateRequest, _=Depends(require_supervisor_or_admin)):
    return create_milestone_issue_entry(payload)


@router.patch("/{task_id}/inactive", summary="Inactivar tarea (auditoria)", response_model=TaskInactiveResponse)
def inactivate_task(task_id: int, _=Depends(require_supervisor_or_admin)):
    return set_task_inactive(task_id)
