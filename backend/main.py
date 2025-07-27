from fastapi import FastAPI
from app.api import auth, admin_servers, client_dashboard




app = FastAPI(
    title="Flussonic Management API",
    description="API for managing Flussonic servers, clients, and stream data.",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_servers.router, prefix="/api/admin/servers", tags=["admin-servers"])
app.include_router(client_dashboard.router, prefix="/api/client", tags=["client"])


@app.get("/")


def read_root():
    return {"message": "Welcome to the Flussonic Management API"}
