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
def get_one_product(product_id:int):
    # product = None

    for oneProduct in products:
        if oneProduct.get("id") == product_id:
            return oneProduct
        
    return{
        "error"
    }
@app.get("/greet")
def greet_user(name:str):
    return{
        "greet":f"helo {name} , how are you?"
    }
    
    # return {
    #     "id":product_id
    # }