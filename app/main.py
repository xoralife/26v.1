from fastapi import FastAPI
from mockData import products
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/pro")
def get_products():
    return products