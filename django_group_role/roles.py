import inspect
from functools import partialmethod, reduce
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from .signals import post_role_setup, pre_role_setup
from .utils import get_permission, map_permissions


class _RoleRegistry(dict):
    def __delitem__(self, v):
        raise NotImplementedError

    def __setitem__(self, k, v):
        if k in self:
            raise ValueError(f"{k} already bound to role registry")
        super().__setitem__(k, v)


# registry which stores the list of available roles
registry = _RoleRegistry()
registry._loaded = False


class RegisterRoleMeta(type):
    @classmethod
    def _get_declared_permissions(cls, bases, classdict):
        permissions = classdict.get("permissions", ())
        # merge permissions with base classes
        permissions = [permissions]
        if bases:
            permissions = reduce(
                lambda a, b: a + [getattr(b, "_permissions", None)],
                bases,
                permissions,
            )
        permissions = map_permissions(*permissions)
        assert not bases or permissions, "A Role must specify at least 1 permission"
        return permissions

    def __new__(cls, classname, bases, classdict, **kwargs):
        name = classdict.get("name", None)
        assert (
            not bases or isinstance(name, str) and name
        ), "Role name must not be empty"
        classdict["_permissions"] = cls._get_declared_permissions(bases, classdict)
        # stop inheritance of abstractness
        is_abstract = classdict.setdefault("abstract", False)
        role_class = super().__new__(cls, classname, bases, classdict, **kwargs)
        if not is_abstract:
            # add role to register
            registry[role_class.name] = role_class

        return role_class


class Role(metaclass=RegisterRoleMeta):
    """Base role class. Every role must inherit from this."""

    name: str = None
    permissions: dict | list | tuple = ()
    abstract = True

    @cached_property
    def group(self):
        from django.contrib.auth.models import Group

        group, _created = Group.objects.get_or_create(name=self.name)
        return group

    @classmethod
    def iter_perms(cls):
        for app_label, app_perms in cls._permissions.items():
            for modelname, perms in app_perms.items():
                for perm in sorted(perms):
                    yield get_permission(perm, app_label, modelname)

    def setup_permissions(self, clear=False):
        """Assignes declared permissions to this role group.

        Args:
            clear (bool, optional): If passed as True also clears existing
                permissions bound to this role. Defaults to False.
        """
        pre_role_setup.send(self.__class__, role=self, clear=clear)
        if clear:
            self.group.permissions.set(self.iter_perms())
        else:
            self.group.permissions.add(*self.iter_perms())
        post_role_setup.send(self.__class__, role=self)

    # wrappers for group methods
    def _wrap_group_method(self, method, *args, **kwargs):
        method = getattr(self.group.user_set, method)
        return method(*args, **kwargs)

    add = partialmethod(_wrap_group_method, method="add")
    remove = partialmethod(_wrap_group_method, method="remove")
    set = partialmethod(_wrap_group_method, method="set")
    clear = partialmethod(_wrap_group_method, method="clear")

    def has_perm(self, perm: str) -> bool:
        # split perm in app and codename
        app_label, codename = perm.split(".", 1)
        if app_label in self._permissions:
            # just check if codename is in any model permission for provided app
            return any(
                codename in perms for perms in self._permissions[app_label].values()
            )
        return False

    def has_perms(self, *perms) -> bool:
        return all(self.has_perm(p) for p in perms)

    def has_any_perm(self, *perms) -> bool:
        return any(self.has_perm(p) for p in perms)


def load_roles(*, force=False, clear=False) -> _RoleRegistry:
    """Force roles to be loaded and returns the updated role registry."""
    from django.conf import settings

    role_module = getattr(settings, "ROLES_MODULE", None)
    if not role_module:
        raise ImproperlyConfigured(
            "ROLES_MODULE settings is required to correctly load roles!"
        )

    # avoid to reload the registry if not needed
    if force or not registry._loaded:
        if clear:
            registry.clear()

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
                and candidate.name not in registry
                # do not register abstract roles
                and not candidate.abstract
                # avoid base class to be added to registry
                and candidate is not Role
            ):
                registry[candidate.name] = candidate

        registry._loaded = True
    return registry
