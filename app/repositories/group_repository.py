from app.repositories.base_repository import SARepository
from app.db.models import Group, User

class GroupRepository(SARepository):
    model = Group
    

    async def add_member(self, member: User, group: Group) -> None:
        group.members.append(member)


    async def delete_member(self, member: User, group: Group) -> None:
        group.members.remove(member)    


    async def get_members(self, group: Group):
        # await self.session.refresh(group)
        result = group.members
        return result
    
    