from fastapi import FastAPI
from starlette.responses import RedirectResponse

from api.interface_adapters.controllers import login, repos, users

app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})
app.include_router(login.router)
app.include_router(repos.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return RedirectResponse(app.docs_url)
