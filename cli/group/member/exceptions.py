from models.group import Group
from models.user import User


class MemberChangeError(RuntimeError):
    def __init__(self, group: Group, user: User, exception: Exception) -> None:
        self.group = group
        self.user = user
        super().__init__(str(exception))
