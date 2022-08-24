from .exceptions import BadRoleException
from .roles import Role, registry
from .signals import post_role_setup, pre_role_setup

__version__ = (0, 4, 0)
