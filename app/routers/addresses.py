""" HTTP layer for Addresses. """


import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session
from app import repository
from app.db import get_db
from app.models import Address
from app.schemas import AddressCreate, AddressRead, AddressUpdate, AddressWithDistance


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/addresses", tags=["addresses"])
DbSession = Annotated[Session, Depends(get_db)]
AddressId = Annotated[int, Path(gt=0, description="Address id.")]

def _get_or_404(db: Session, address_id: int) -> Address:
    """ Get ID or return 'Not Found' code error. """
    
    address = repository.get_address(address_id)
    if address is None:
        logger.warning("Address ID not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address {address_id} not found. ")

    return address

@router.post("", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(db: DbSession, payload: AddressCreate) -> Address:
    """ Endpoint/function for 'POST' method. """
    
    return repository.create_address(db, payload)

@router.get("", response_model=list[AddressRead])
def list_addresses(db: DbSession, skip: Annotated[int, Query(ge=0)] = 0, limit: Annotated[int, Query(ge=1, le=100)] = 50) -> list[Address]:
    """ Endpoint/function for 'GET' method. """
    
    return list(repository.list_addresses(db, skip=skip, limit=limit))


@router.get("/nearby", response_model=list[AddressWithDistance])
def find_nearby(db: DbSession, latitude: Annotated[float, Query(ge=-90, le=90)], longitude: Annotated[float, Query(ge=-180, le=180)], distance_km: Annotated[float, Query(gt=0, le=20_000)]) -> list[AddressWithDistance]:
    """ Endpoint/function for 'GET' method with 'nearby' query params. """

    nearby_results = repository.find_nearby(db, latitude, longitude, distance_km)
    return [
        AddressWithDistance(**AddressRead.model_validate(address).model_dump(), distance_km=round(distance, 3)) for address, distance in nearby_results
    ]

@router.get("/{address_id}", response_model=AddressRead)
def get_address(db: DbSession, address_id: AddressId) -> Address:
    """ Endpoint/function for 'GET' method with ID. """
    
    return _get_or_404(db, address_id)

@router.patch("/{address_id}", response_model=AddressRead)
def update_address(db: DbSession, address_id: AddressId, payload: AddressUpdate):
    """ Endpoint/function for 'PATCH'(preferred over PUT) method with ID. """

    result = _get_or_404(db, address_id)

    return repository.update_address(db, result)

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(db: DbSession, address_id: AddressId) -> Response:
    """ Endpoint/function for 'DELETE' method with ID."""

    result = _get_or_404(db, address_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)