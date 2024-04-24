from app.repositories.base_repository import SARepository
from app.db.models import User

class UserRepository(SARepository):
    model = User

    