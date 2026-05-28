from pydantic import BaseModel, ConfigDict


class TransitRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_code: str
    name: str
    description: str | None = None
