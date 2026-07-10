def greet(*args):
    return f"Hello, {' '.join(args)}!"

settings = {"host":"db","port":5432}

connect(*args, **kwargs):
    host = kwargs.get("host", settings["host"])
    port = kwargs.get("port", settings["port"])


router = APIRouter(prefix="/api",tags=["utils"])

@router.get("/ping")
def ping():
    return {"pong":True}