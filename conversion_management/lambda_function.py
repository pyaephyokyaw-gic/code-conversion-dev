from fastapi import FastAPI
from mangum import Mangum
from .controllers.conversion_controller import router

app = FastAPI(title="conversion result management")

app.include_router(router)
handler = Mangum(app)
