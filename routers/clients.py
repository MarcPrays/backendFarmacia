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

routerClient = APIRouter(prefix="/clients", tags=["Clients"])


@routerClient.post("/", response_model=ClientResponse)
def create_client_endpoint(data: ClientCreate, db: Session = Depends(get_db)):
    return create_client(db, data)


@routerClient.get("/all", response_model=list[ClientResponse])
def list_clients(db: Session = Depends(get_db)):
    return get_clients(db)


@routerClient.get("/{client_id}", response_model=ClientResponse)
def get_client_endpoint(client_id: int, db: Session = Depends(get_db)):
    client = get_client(db, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    return client


@routerClient.put("/{client_id}", response_model=ClientResponse)
def update_client_endpoint(client_id: int, data: ClientUpdate, db: Session = Depends(get_db)):
    updated = update_client(db, client_id, data)
    if not updated:
        raise HTTPException(404, "Client not found")
    return updated


@routerClient.delete("/{client_id}")
def delete_client_endpoint(client_id: int, db: Session = Depends(get_db)):
    deleted = delete_client(db, client_id)
    if not deleted:
        raise HTTPException(404, "Client not found")
    return {"message": "Client deleted successfully"}
