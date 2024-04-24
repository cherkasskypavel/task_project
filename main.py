from fastapi import FastAPI
import uvicorn

from app.api.endpoints.admin import admin
from app.api.endpoints.users import auth
from app.api.endpoints.tasks import tasks
from app.api.endpoints.dashboard import dashboard


app = FastAPI()


app.include_router(auth)
app.include_router(admin)
app.include_router(tasks)
app.include_router(dashboard)


if __name__ == '__main__':
    uvicorn.run(app)    

   