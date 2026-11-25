from datetime import datetime
from typing import Annotated, Self
from pydantic import BaseModel, ConfigDict, Field, model_validator

Label = Annotated[str, Field(min_length=1, max_length=100)]
Street = Annotated[str, Field(min_length=1, max_length=255)]
City = Annotated[str, Field(min_length=1, max_length=100)]
PostalCode = Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[A-Za-z0-9 \-]+$")]
Country = Annotated[str, Field(min_length=2, max_length=100)]
Latitude = Annotated[float, Field(ge=-90, le=90, description="Latitude in decimal degrees.", examples=[14.5831])]
Longitude = Annotated[float, Field(ge=-180, le=180, description="Latitude in decimal degrees.", examples=[14.5831])]


class AddressBase(BaseModel):
    """ Address base model. """
    model_config = ConfigDict(str_strip_whitespace=True)

    label: Label | None = None
    street: Street
    city: City
    postal_code: PostalCode | None = None
    country: Country
    latitude: Latitude
    longitude: Longitude


class AddressCreate(AddressBase):
    """ (C)reate Address. """


class AddressRead(AddressBase):
    """ (R)ead Address. """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AddressWithDistance(AddressRead):
    """ Address distance base search. """

    distance_km: float = Field(description="Distance in kilometers.")


class AddressUpdate(BaseModel):
    """ (U)pdate Address"""

    model_config = ConfigDict(str_strip_whitespace=True)


    label: Label | None = None
    street: Street | None = None
    city: City | None = None
    postal_code: PostalCode | None = None
    country: Country | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")

        nullable = {"label", "postal_code"}
        nulled = sorted(
            field for field in self.model_fields_set - nullable if getattr(self, field) is None
        )
        if nulled:
            raise ValueError(f"The following fields cannot be NULL: {', '.join(nulled)}")

        return self
