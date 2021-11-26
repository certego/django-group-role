from functools import reduce, partialmethod
import inspect
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured, MultipleObjectsReturned
from .exceptions import BadRoleException
from .utils import map_permissions

try:  # prefer python builtin cached_property
    from functools import cached_property
except ImportError:
    from django.utils.functional import cached_property


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
        permissions = classdict.get("permissions", [])
        # merge permissions with base classes
        permissions = [permissions]
        if bases:
            permissions = reduce(
                lambda a, b: a + [getattr(b, "permissions", None)], bases, permissions
            )
        permissions = map_permissions(*permissions)
        assert not bases or permissions, "A Role must specify at least 1 permission"
        return permissions

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
        if not classdict.get("abstract", False):
            # add role to register
            registry[role_class._group] = role_class

        return role_class


class Role(metaclass=RegisterRoleMeta):
    """Base role class. Every role must inherit from this."""

    name: str = None
    permissions = []
    abstract = True

    @cached_property
    def group(self):
        from django.contrib.auth.models import Group

        group, _created = Group.objects.get_or_create(name=self._group)
        return group

    def setup_permissions(self, clear=False):
        """Assignes declared permissions to this role group.

        Args:
            clear (bool, optional): If passed as True also clears existing permissions bound to this role. Defaults to False.
        """
        from django.contrib.auth.models import Permission
        from guardian.shortcuts import assign_perm

        if clear:
            self.group.permissions.clear()

        for app_label, app_perms in self._permissions.items():
            for modelname, perms in app_perms.items():
                if modelname == "_codenames":
                    # handle codenames permissions
                    for perm in perms:
                        perm = f"{app_label}.{perm}"
                        try:
                            assign_perm(perm, self.group)
                        except (
                            ValueError,
                            Permission.DoesNotExist,
                            MultipleObjectsReturned,
                        ):
                            raise BadRoleException(
                                f"Permission {perm} cannot be bound to role", perm
                            )
                else:
                    # model-grouped perms
                    for perm in perms:
                        try:
                            perm = Permission.objects.get_by_natural_key(
                                perm, app_label, modelname
                            )
                        except (ValueError, Permission.DoesNotExist):
                            raise BadRoleException(
                                f"Permission {perm} ({app_label})  cannot be bound to role",
                                f"{app_label}.{perm}",
                            )
                        else:
                            assign_perm(perm, self.group)

    # wrappers for group methods
    def _wrap_group_method(self, method, *args, **kwargs):
        method = getattr(self.group, method)
        return method(*args, **kwargs)

    add = partialmethod(_wrap_group_method, method="add")
    remove = partialmethod(_wrap_group_method, method="remove")
    set = partialmethod(_wrap_group_method, method="set")
    clear = partialmethod(_wrap_group_method, method="clear")


def load_roles():
    from django.conf import settings

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
