from fastapi import HTTPException

from secureapi.repositories.task_repository import (
    create_milestone_issue,
    create_task,
    deactivate_task,
    list_milestone_issues,
    list_tasks_for_supervisor,
    list_tasks_for_user,
    update_task_status,
)
from secureapi.repositories.user_repository import get_user_by_username


def create_task_for_user(payload, creator_user):
    assigned_user = get_user_by_username(payload.assigned_to_username)
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

    if assigned_user["role"] != "usuario_comun":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden asignar tareas a usuarios con rol usuario_comun",
        )

    task_id = create_task(
        title=payload.title,
        description=payload.description,
        milestone=payload.milestone,
        issue_type=payload.issue_type,
        milestone_issue_id=payload.milestone_issue_id,
        assigned_to=assigned_user["id"],
        created_by=creator_user["id"],
        due_at=payload.due_at,
    )

    return {
        "id": task_id,
        "title": payload.title,
        "assigned_to": payload.assigned_to_username,
        "status": "no_iniciada",
        "due_at": payload.due_at,
    }


def get_task_board_for_supervisor(status: str | None = None, assigned_to_username: str | None = None):
    return list_tasks_for_supervisor(status=status, assigned_to_username=assigned_to_username)


def get_task_board_for_user(user_id):
    return list_tasks_for_user(user_id)


def update_user_task_status(task_id, user_id, status, notes):
    if not update_task_status(task_id=task_id, user_id=user_id, status=status, progress_notes=notes):
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada, inactiva o no asignada a este usuario",
        )
    return {"message": "Estado de tarea actualizado", "task_id": task_id, "status": status}


def create_milestone_issue_entry(payload):
    issue_id = create_milestone_issue(payload.milestone, payload.issue_type, payload.description)
    return {
        "id": issue_id,
        "milestone": payload.milestone,
        "issue_type": payload.issue_type,
        "description": payload.description,
    }


def get_milestone_issue_catalog():
    return list_milestone_issues()


def set_task_inactive(task_id):
    if not deactivate_task(task_id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada o ya inactiva")
    return {"message": "Tarea inactivada", "task_id": task_id}
