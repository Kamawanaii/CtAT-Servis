from fastapi import FastAPI, UploadFile
import pandas as pd

app = FastAPI()

products = []

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/products")
def get_products():
    return products

@app.post("/upload")
def upload(file: UploadFile):
    global products
    df = pd.read_excel(file.file)
    products = df.to_dict(orient="records")
    return {"status": "ok"}