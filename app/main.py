from fastapi import FastAPI
from mockData import products


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}


@app.get("product")
def get_products():
    return products


@app.get("/product/{product_id}")
def get_one_product(product_id:int):
    # product = None

    for oneProduct in product:
        if oneProduct.get("id") == product_id:
            return oneProduct
        
    return{
        "error"
    }

    
    # return {
    #     "id":product_id
    # }