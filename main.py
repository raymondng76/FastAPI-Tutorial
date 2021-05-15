from enum import Enum
from fastapi import FastAPI

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

