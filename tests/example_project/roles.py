from django_group_role import Role


class BasicRole(Role):
    name = "Users"
    permissions = ["auth.view_user", "auth.view_group"]


class UserManagers(BasicRole):
    name = "User-Managers"
    permissions = ["auth.add_user", "auth.change_user"]


class GroupManagers(BasicRole):
    name = "Group Managers"
    permissions = ["auth.add_group", "auth.view_group", "auth.delete_group"]


class GroupPermManagers(GroupManagers):
    name = "Top-Managers"
    permissions = [
        "auth.add_permission",
        "auth.view_permission",
        "auth.delete_permission",
    ]


class AbstractRole(Role):
    name = "Abstract"
    abstract = True
    permissions = ["auth.add_group", "auth.view_group", "auth.delete_group"]


class Erasers(Role):
    name = "Erasers"
    permissions = {
        "auth": {
            "user": ["delete_user"],
            "group": ["delete_group"],
            "permission": ["delete_permission", "broken"],
        }
    }


class BrokenRole(Role):
    name = "Broken"
    permissions = ["auth.non_existing_perm"]
