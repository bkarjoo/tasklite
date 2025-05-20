from fastapi import FastAPI
from data.db_session import engine
from data.models.alchemy_base import Base
from routes import task_routes

app = FastAPI()
app.include_router(task_routes.router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "TaskLite is up"}
