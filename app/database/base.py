# Import all the models, so that Base has them before being
# imported by Alembic
from app.database.session import Base  # noqa
from app.models.user_model import UserModel  # noqa
from app.models.todo_model import TodoModel  # noqa
from app.models.refresh_token_model import RefreshTokenModel  # noqa
