""" DB Transactions ONLY. """


import logging
from collections.abc import Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select
from app import geo
from app.models import Address
from app.schemas import AddressCreate, AddressUpdate


logger = logging.getLogger(__name__)

def create_address(db: Session, data: AddressCreate) -> Address:
    """ Insert new address, persist, return along with ID. """
    
    address = Address(**data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)

    logger.info("Created address id=%s", address.id)

    return address

def get_address(db: Session, address_id: int) -> Address | None:
    """ Get existing address OR return None. """

    return db.get(Address, address_id)

def list_addresses(db: Session, skip: int = 0, limit: int = 50) -> Sequence[Address]:
    """ Get all addresses sorted by ID with limit amount of results."""

    query = select(Address).order_by(Address.id).offset(skip).limit(limit)

    return db.scalars(query).all()

def update_address(db: Session, address: Address, data: AddressUpdate) -> Address:
    """ Update details/field values of a given Address. """

    changes = data.model_dump(exclude_unset=True)
    
    for field, value in changes.items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    logger.info("Updated address id=%s fields=%s", address.id, sorted(changes))
    
    return address

def delete_address(db: Session, address: Address) -> None:
    """ Delete an Address. """

    address_id = address.id
    db.delete(address)
    db.commit()
    logger.info("Deleted address of ID=%s", address_id)


def find_nearby(db: Session, latitude: float, longitude: float, distance_km: float) -> list[tuple[Address, float]]:
    """ Get nearby Addresses. """

    nearby_results: list[tuple[Address, float]] = []
    box = geo.bounding_box(latitude, longitude, distance_km)
    query = (select(Address)
        .where(
            Address.latitude.between(box.min_lat, box.max_lat), 
            Address.longitude.between(box.min_lon, box.max_lon)
        )
    )

    results = db.scalars(query).all()
    for result in results:
        distance = geo.haversine_km(latitude, longitude, result.latitude, result.longitude)
        if distance <= distance_km:
            nearby_results.append((result, distance))
    results.sort(key=lambda pair: pair[1])

    logger.debug("Nearby search (%s, %s, %skm): %d results.", latitude, longitude, distance_km, len(results))

    return results