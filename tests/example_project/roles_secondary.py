from django_group_role.roles import Role


class Base(Role):
    name = "Base"
    permissions = ["auth.view_user", "auth.view_group"]


class UserManagers(Base):
    name = "Managers"
    permissions = ["auth.add_user", "auth.change_user"]


class GroupManagers(Base):
    name = "Groupers"
    permissions = ["auth.add_group", "auth.view_group", "auth.delete_group"]
