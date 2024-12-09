from sqlalchemy.orm import Session
from app.db.models import Court

def create_court(db: Session, court_data: dict):
    court = Court(**court_data)
    db.add(court)
    db.commit()
    db.refresh(court)
    return court

def get_all_courts(db: Session):
    return db.query(Court).all()

def get_court_by_id(db: Session, court_id: str):
    return db.query(Court).filter(Court.id == court_id).first()

def update_court(db: Session, court_id: str, updates: dict):
    court = db.query(Court).filter(Court.id == court_id).first()
    for key, value in updates.items():
        setattr(court, key, value)
    db.commit()
    db.refresh(court)
    return court

def delete_court(db: Session, court_id: str):
    court = db.query(Court).filter(Court.id == court_id).first()
    db.delete(court)
    db.commit()
    return court
