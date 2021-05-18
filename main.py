from enum import Enum
from typing import Dict, List, Optional, Set

from fastapi import Body, Cookie, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl

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


# ----------
@app.get("/items11/")
async def items11(
    q: Optional[str] = Query(None, min_length=3, max_length=50, regex="^fixedquery$")
):  # User Query for additional validation, first param set default values,
    # None means optional, min_length and max_length limits length for q,
    # regex: ^ means start with following chars, fixedquery means exact value fixedquery,
    # $ ends there, no more chars after fixedquery
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items12/")
async def items12(
    q: str = Query(..., min_length=3, max_length=50)
):  # Query first param means default, ... means non-optional, q param is required
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# localhost:8000/items13/?q=foo&q=bar&q=woot
@app.get("/items13/")
async def items13(
    q: Optional[List[str]] = Query(None),
):  # Optional List accepts multiple input by declaring q multiple times
    query_items = {"q": q}
    # {
    #     "q": [
    #         "foo",
    #         "bar",
    #         "woot"
    #     ]
    # }
    return query_items


@app.get("/items14/")
async def items14(
    q: List[str] = Query(["foo", "bar", "woot"], title="Query string", min_length=3)
):  # Required list, default values are declared inside Query
    # Can also just use q: list = Query([])
    query_items = {"q": q}
    return query_items


# for example you want parameter to be item-query
# localhost:8000/items15/?item-query=foobaritem
# this way, Query will help to match item-query and assign correctly to q
@app.get("/items15/")
async def items15(q: Optional[str] = Query(None, alias="item-query")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Add deprecated args = True to indicate endpoint is deprecated
# Will showup in Swagger
@app.get("/items16/")
async def items16(q: Optional[str] = Query(None, deprecated=True)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# ----------
@app.get("/items17/{item_id}")
async def items17(
    item_id: int = Path(
        ..., title="The ID of item to get"
    ),  # path parameter is always required, use ... as placeholder
    q: Optional[str] = Query(
        None, alias="item-query"
    ),  # move q to first pos if it doesnt have default
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# If order of args matter and q without default needs to be last, use * in the first pos
@app.get("/items18/{item_id}")
async def items18(*, item_id: int = Path(..., title="The ID"), q: str):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Both Query and Path can use string/number validation
@app.get("/items19/{item_id}")
async def items19(
    *,
    item_id: int = Path(..., title="ID", ge=0, le=1000),
    q: str,
    size: float = Query(..., gt=0, lt=10),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# ----------
class Item2(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.put("/items20/{item_id}")
async def items20(
    *,
    item_id: int = Path(..., title="ID", ge=0, le=1000),
    q: Optional[str] = None,
    item: Optional[Item2] = None,  # can set body parameter as optional
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


# Body
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     }
# }


@app.put("/items21/{item_id}")
async def items21(item_id: int, item: Item2, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     },
#     "importance": 5
# }


@app.put("/items22/{item_id}")
async def items22(
    item_id: int, item: Item2, user: User, importance: int = Body(...)
):  # use Body(...) for singular value body
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.put("/items23/{item_id}")
async def items23(
    *,
    item_id: int,
    item: Item2,
    user: User,
    importance: int = Body(..., gt=0),  # Body also support validation
    q: Optional[str] = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


# Expect body like this
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     }
# }
# instead of this
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2
# }


@app.put("/items24/{item_id}")
async def items24(item_id: int, item: Item2 = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


# ----------
class Item3(BaseModel):
    name: str
    description: Optional[str] = Field(  # field works the same as Query, Path and Body
        None, title="item", max_length=300
    )
    price: float = Field(..., gt=0, description="price > 0")
    tax: Optional[float] = None


@app.put("/items25/{item_id}")
async def items25(item_id: int, item: Item3 = Body(..., embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


# ----------


class Item4(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: list = []  # define list attribute or use the List typing for type hint
    # tags: List[str] = []
    # tags: Set[str] = set()    for using set


@app.put("/items26/{item_id}")
async def items26(item_id: int, item: Item4):
    results = {"item_id": item_id, "item": item}
    return results


# ----------
class Image1(BaseModel):
    # url: str
    url: HttpUrl  # use HttpUrl for URL validation, else use string above
    name: str


class Item5(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: Set[str] = set()
    image: Optional[Image1] = None  # Use Image1 type


# Body
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": ["rock", "metal", "bar"],
#     "image": {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }
# }


@app.put("/items27/{item_id}")
async def items27(item_id: int, item: Item5):
    results = {"item_id": item_id, "item": item}
    return results


# Body
# {
#     "name": "Foo",
#     "description": "The pretender",
#     "price": 42.0,
#     "tax": 3.2,
#     "tags": [
#         "rock",
#         "metal",
#         "bar"
#     ],
#     "images": [
#         {
#             "url": "http://example.com/baz.jpg",
#             "name": "The Foo live"
#         },
#         {
#             "url": "http://example.com/dave.jpg",
#             "name": "The Baz"
#         }
#     ]
# }


class Item6(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: Set[str] = set()
    images: Optional[List[Image1]] = None


@app.put("/items28/{item_id}")
async def items28(item_id: int, item: Item6):
    results = {"item_id": item_id, "item": item}
    return results


class Offer1(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item6]  # Deep nested models


@app.post("/offers1/")
async def offers1(offer: Offer1):
    return offer


# [
#     {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     },
#     {
#         "url": "http://example.com/dave.jpg",
#         "name": "The Baz"
#     }
# ]


@app.post("/images1/multiple")
async def images1(images: List[Image1]):  # JSON body with a list at the top level value
    return images


# {
#     1: 1.1,
#     2: 2.2
# }


@app.post("/index-weights1")
async def index_weights1(weights: Dict[int, float]):
    return weights


# ----------


class Item7(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

    class Config:  # keyword for pydantic
        schema_extra = {  # keyword for pydantic
            "example": {  # example will show up in JSON schema
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@app.put("/items29/{item_id}")
async def items29(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


class Item8(BaseModel):
    name: str = Field(..., example="Foo")  # Example stated will pass to JSON schema
    description: Optional[str] = Field(None, example="A very nice item")
    price: float = Field(..., example=35.4)
    tax: Optional[float] = Field(None, example=3.2)


@app.put("/items30/{item_id}")
async def items30(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


@app.put("/items31/{item_id}")
async def items31(
    item_id: int,
    item: Item7 = Body(
        ...,
        example={  # declare examples straight in the Body
            "name": "Foo",
            "description": "A very nice item",
            "price": 35.4,
            "tax": 3.2,
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


@app.put("/items32/{item_id}")
async def items32(
    *,
    item_id: int,
    item: Item7 = Body(
        ...,
        examples={ # multiple examples, shown as dropdown in Swagger UI
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly",
                "value": {
                    "name": "Foo",
                    "description": "A very nice item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "convert price to actual num",
                "value": {  # description and tax optional
                    "name": "Bar",
                    "price": "35.3",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


# ----------

@app.get("/items33/")
async def items33(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}
