from enum import Enum
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI object instance
app = FastAPI()

# ----------
# Root end point
@app.get("/")
async def root():
    return {"message": "Hello World"}


# ----------
# Dynamic input
# localhost:8000/items/42/
@app.get("/items/{item_id}")  # item_id from address path -> input args item_id
async def read_item(item_id: int):  # auto type validation with type hints
    return {"item_id": item_id}


# Static input
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


# Dynamic address str type
@app.get("/users/{user_id}")
async def read_user(user_id: str):  # String type
    return {"user_id": user_id}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(
    model_name: ModelName,
):  # Use Enum to constraint available types and values
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


@app.get(
    "/files/{file_path:path}"
)  # :path indicate match any path (i.e. /files//home/johndoe/myfiles.txt)
async def read_file(file_path: str):
    return {"file_path": file_path}


# ----------
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# localhost:8000/items2/?skip=0&limit=10
@app.get("/items2/")
async def items2(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.get("/items3/{item_id}")
async def items3(
    item_id: str, q: Optional[str] = None
):  # FastAPI knows optional because of `= None`, Optional is only for editor static check
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# localhost:8000/items4/foo?short=True
# localhost:8000/items4/foo?short=true
# localhost:8000/items4/foo?short=1   -> truthy
# localhost:8000/items4/foo?short=on  -> truthy
# localhost:8000/items4/foo?short=yes -> truthy
@app.get("/items4/{item_id}")
async def item4(item_id: str, q: Optional[str] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "long description"})
    return item


# localhost:8000/items5/foo?needy=soneedy
@app.get("/items5/{item_id}")
async def items5(item_id: str, needy: str):  # required parameters
    item = {"item_id": item_id, "needy": needy}
    return item


# localhost:8000/item6/foo?needy=soneedy&skip=0&limit=0
@app.get("/items6/{item_id}")
async def items6(
    item_id: str, needy: str, skip: int = 0, limit: Optional[int] = None
):  # needy = required str, skip = required int with default 0, limit = optional int
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


# ----------


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


# Body
# {
#   "name": "some name",
#   "prince": 50.1
# }
# {
#   "name": "some name",
#   "prince": 50.1,
#   "description": "some description",
#   "tax": "100"
# }
@app.post("/items7/")
async def items7(item: Item):  # expect fields from inside the Item class
    return item


@app.post("/items8")
async def items8(item: Item):
    item_dict = item.dict()  # convert item json to dict first
    if item.tax:  # use dot notation or indexing to access
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items9/{item_id}")
async def items9(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}  # Unroll dict


# localhost:8000/100/?q=foo
@app.put("/items10/{item_id}")
async def items10(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
