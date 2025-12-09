from sqlalchemy.orm import Session
from db.models import Client
from db.schemas import ClientCreate, ClientUpdate


def create_client(db: Session, data: ClientCreate):
    client = Client(
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_clients(db: Session):
    return db.query(Client).filter(Client.status == 1).all()


def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()


def update_client(db: Session, client_id: int, data: ClientUpdate):
    client = get_client(db, client_id)
    if not client:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int) -> bool:
    client = get_client(db, client_id)
    if not client:
        return False

    client.status = 0
    db.commit()
    return True
