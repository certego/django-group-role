from django_group_role.roles import Role


class BasicRole(Role):
    name = "Users"
    permissions = ["auth.view_user", "auth.view_group"]


class UserManagers(BasicRole):
    name = "User-Managers"
    permissions = ["auth.add_user", "auth.change_user"]


class GroupManagers(BasicRole):
    name = "Group-Managers"
    permissions = ["auth.add_group", "auth.view_group", "auth.delete_group"]


class BrokenRole(Role):
    name = "Broken"
    permissions = ["auth.non_existing_perm"]
