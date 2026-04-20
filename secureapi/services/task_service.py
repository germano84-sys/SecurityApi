from fastapi import HTTPException

from repositories.task_repository import (
    complete_task,
    create_task,
    deactivate_task,
    list_tasks_for_supervisor,
    list_tasks_for_user,
)
from repositories.user_repository import get_user_by_username


def create_task_for_user(payload, creator_user):
    assigned_user = get_user_by_username(payload.assigned_to_username)
    if not assigned_user:
        raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

    task_id = create_task(
        title=payload.title,
        description=payload.description,
        milestone=payload.milestone,
        issue_type=payload.issue_type,
        assigned_to=assigned_user["id"],
        created_by=creator_user["id"],
        due_at=payload.due_at,
    )

    return {
        "id": task_id,
        "title": payload.title,
        "assigned_to": payload.assigned_to_username,
        "status": "pendiente",
        "due_at": payload.due_at,
    }


def get_task_board_for_supervisor():
    return list_tasks_for_supervisor()


def get_task_board_for_user(user_id):
    return list_tasks_for_user(user_id)


def complete_user_task(task_id, user_id, completion_notes):
    if not complete_task(task_id=task_id, user_id=user_id, completion_notes=completion_notes):
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada, inactiva o no asignada a este usuario",
        )
    return {"message": "Tarea finalizada", "task_id": task_id}


def set_task_inactive(task_id):
    if not deactivate_task(task_id):
        raise HTTPException(status_code=404, detail="Tarea no encontrada o ya inactiva")
    return {"message": "Tarea inactivada", "task_id": task_id}
