from functools import reduce, partialmethod
import inspect
from importlib import import_module
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import (
    ImproperlyConfigured,
    ObjectDoesNotExist,
    MultipleObjectsReturned,
)
from guardian.shortcuts import assign_perm

try:  # prefer python builtin cached_property
    from functools import cached_property
except ImportError:
    from django.utils.functional import cached_property


class BadRoleException(Exception):
    def __init__(self, message, permission):
        self.permission = permission
        super().__init__(message)


class _RoleRegistry(dict):
    def __delitem__(self, v):
        raise NotImplementedError

    def __setitem__(self, k, v):
        if k in self:
            raise ValueError(f"{key} already bound to role registry")
        super().__setitem__(k, v)


# registry which stores the list of available roles
registry = _RoleRegistry()


class RegisterRoleMeta(type):
    @classmethod
    def _get_declared_permissions(cls, bases, classdict):
        permissions = classdict.pop("permissions", [])
        assert not bases or isinstance(
            permissions, (list, tuple, set)
        ), "Role permissions must be a list a set or a tuple"
        assert all(
            isinstance(p, str) for p in permissions
        ), "Permissions must be represented with strings"
        # merge permissions with base classes
        if bases:
            permissions += reduce(
                lambda a, b: a + getattr(b, "_permissions"), bases, []
            )
        assert not bases or permissions, "A Role must specify at least 1 permission"
        return list(set(permissions))

    @classmethod
    def _get_declared_group_name(cls, bases, classdict):
        name = classdict.pop("name", None)
        assert (
            not bases or isinstance(name, str) and name
        ), "Role name must not be empty"
        return name

    def __new__(cls, classname, bases, classdict, **kwargs):
        classdict["_group"] = cls._get_declared_group_name(bases, classdict)
        classdict["_permissions"] = cls._get_declared_permissions(bases, classdict)
        role_class = super().__new__(cls, classname, bases, classdict, **kwargs)
        if bases:
            # add role to register
            registry[role_class._group] = role_class

        return role_class


class Role(metaclass=RegisterRoleMeta):
    """Base role class. Every role must inherit from this."""

    name: str = None
    permissions = set()

    @cached_property
    def group(self):
        group, _created = Group.objects.get_or_create(name=self._group)
        return group

    def setup_permissions(self, clear=False):
        """Assignes declared permissions to this role group.

        Args:
            clear (bool, optional): If passed as True also clears existing permissions bound to this role. Defaults to False.
        """
        if clear:
            self.group.permissions.clear()

        for perm in self._permissions:
            try:
                assign_perm(perm, self.group)
            except (ValueError, ObjectDoesNotExist, MultipleObjectsReturned):
                raise BadRoleException(
                    f"Permission {perm} cannot be bound to role", perm
                )

    # wrappers for group methods
    def _wrap_group_method(self, method, *args, **kwargs):
        method = getattr(self.group, method)
        return method(*args, **kwargs)

    add = partialmethod(_wrap_group_method, method="add")
    remove = partialmethod(_wrap_group_method, method="remove")
    set = partialmethod(_wrap_group_method, method="set")
    clear = partialmethod(_wrap_group_method, method="clear")


def load_roles():
    role_module = getattr(settings, "ROLES_MODULE", None)
    if not role_module:
        raise ImproperlyConfigured(
            "ROLES_MODULE settings is required to correctly load roles!"
        )

    try:
        mod = import_module(role_module)
    except ImportError:
        raise ImproperlyConfigured(
            f"No module {role_module} from which import roles found!"
        )

    # get roles by inspecting module
    for name, candidate in inspect.getmembers(mod, inspect.isclass):
        if (
            issubclass(candidate, Role)
            and candidate._group not in registry
            and not candidate is Role  # avoid base class to be added to registry
        ):
            registry[candidate._group] = candidate
