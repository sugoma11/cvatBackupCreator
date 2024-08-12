from pydantic import BaseModel


class BackupRoot(BaseModel):
    shapes: list

    version: int = 0
    tags: list = []
    tracks: list = []


class Polygon(BaseModel):
    frame: int
    label: str
    points: list = []

    type: str = "polygon"
    occluded: bool = False
    outside: bool = False
    z_order: int = 0
    group: int = 0
    source: str = "manual"
    attributes: list = []
    elements: list = []


class Rectangle(BaseModel):
    points: list = []
    frame: int
    label: str

    type: str = "rectangle"
    occluded: bool = False
    outside: bool = False
    z_order: int = 0
    group: int = 0
    source: str = "manual"
    attributes: list = []
    elements: list = []




