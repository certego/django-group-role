from .exceptions import BadRoleException
from .roles import Role, load_roles, registry
from .signals import post_role_setup, pre_role_setup

__version__ = (0, 5, 0)
