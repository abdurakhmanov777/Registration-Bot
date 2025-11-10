from app.routers.admin.callback import router as admin_callback
from app.routers.admin.command import router as admin_command
from app.routers.admin.message import router as admin_message
from app.routers.intercept.intercept import router as intercept
from app.routers.user.callback import router as user_callback
from app.routers.user.command import router as user_command
from app.routers.user.message import router as user_message

__all__: list[str] = [
    "admin_callback",
    "admin_command",
    "admin_message",
    "intercept",
    "user_callback",
    "user_command",
    "user_message",
]
