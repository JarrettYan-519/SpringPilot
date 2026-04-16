from pydantic import BaseModel


class UserConfigSet(BaseModel):
    value: str | None


class UserConfigRead(BaseModel):
    key: str
    value: str | None

    model_config = {"from_attributes": True}


class UserConfigBulkRead(BaseModel):
    configs: dict[str, str | None]
