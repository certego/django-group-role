from .exceptions import BadRoleException
from .roles import Role, load_roles, registry
from .signals import post_role_setup, pre_role_setup


def _get_role(role) -> Role:
    assert isinstance(role, (Role, str))
    if isinstance(role, str):
        load_roles()
        try:
            role = registry[role]
        except KeyError:
            raise BadRoleException(f"Role {role} is not registered")

    return role


def is_user_in_role(user, role) -> bool:
    try:
        role = _get_role(role)
    except BadRoleException:
        # the role is not registered thus we assume the user
        # cannot have that role
        return False

    return user.groups.filter(name=role.name).exists()


__version__ = (0, 7, 4)
