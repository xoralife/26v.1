from fastapi import FastAPI
from mockData import products

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/product")
def get_product():
    return products

@app.get("/product/{product_id}")
def get_one_product(product_id: int):

    for oneProduct in products:
        if int(oneProduct["id"]) == product_id:
            return oneProduct

    return {
        "error": "Product not found"
    }  