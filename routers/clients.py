from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ClientCreate, ClientUpdate, ClientResponse
from crud.clients import (
    create_client,
    get_clients,
    get_client,
    update_client,
    delete_client
)
from utils.auth import get_current_user
from utils.permissions import check_permission
from db.models import User

routerClient = APIRouter(prefix="/clients", tags=["Clients"])


@routerClient.post("/", response_model=ClientResponse)
def create(
    data: ClientCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear cliente - Requiere permiso clients.create"""
    check_permission(db, current_user, "clients.create")
    return create_client(db, data)


@routerClient.get("/all", response_model=list[ClientResponse])
def list_all(
    search: str = None, 
    status: int = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar clientes con filtros - Requiere permiso clients.view"""
    check_permission(db, current_user, "clients.view")
    return get_clients(db, search=search, status=status)


@routerClient.get("/", response_model=ClientResponse)
def get(
    client_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener cliente por ID - Requiere permiso clients.view"""
    check_permission(db, current_user, "clients.view")
    client = get_client(db, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    return client


@routerClient.put("/", response_model=ClientResponse)
def update(
    client_id: int, 
    data: ClientUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar cliente - Requiere permiso clients.edit"""
    check_permission(db, current_user, "clients.edit")
    updated = update_client(db, client_id, data)
    if not updated:
        raise HTTPException(404, "Client not found")
    return updated


@routerClient.delete("/")
def delete(
    client_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar cliente - Requiere permiso clients.delete"""
    check_permission(db, current_user, "clients.delete")
    deleted = delete_client(db, client_id)
    if not deleted:
        raise HTTPException(404, "Client not found")
    return {"message": "Client deleted successfully"}
