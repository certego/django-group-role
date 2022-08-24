# Django Group Role
[![Linters/Tests][ci-badge]][ci]
[![PyPI versions][pypi-badge]][pypi]
[![PyPI pyversions][pythonver]][pypi]
[![Django version][djversion]][pypi]

`django-group-role` aims to simplify "role based access" in django-based projects and applications.
This app is build on top on `contrib.auth` and `guardian` apps.


`django-group-role` aims to enhance existing `Group` and `Permission` models of `contrib.auth` app to configure global-level access rules.

## Install
First add `'django_group_role'` to `INSTALLED_APPS` after `contrib.auth` and `guardian` and then configure the "role-definition" module:

```PYTHON
INSTALLED_APPS = [
    ...
    "django.contrib.auth",
    ...
    "guardian",
    "django_group_role",
    ...
]

# every used role must be registered in this module
ROLES_MODULE = "myproject.roles"
```


## Basic Setup

"Roles" are classes derived from `django_group_role.roles.Role` and should declare the following two attributes:

- `name`: the name of the group which will be bound to this role (mandatory)
- `permissions`: specify which permissions are granted to this role, it may be indicated in one of the following form:
   - a _list_ of available permission which will be bound to this role, they must be provided using the notation `'<appname>.<codename>'`
   - a _dict_ which keys can be app-names or `<appname.model>` (see example below)

```python
from django_group_role import Role


class BasicRole(Role):
    name = "Base"
    abstract = True
    permissions = ["auth.view_user", "auth.view_group"]


class ExpandedRole(BasicRole):
    name = "Expanded"
    permissions = ["auth.add_user", "auth.change_user"]


class DerivedRole(BasicRole):
    name = "Derived"
    permissions = {
        'auth': {
            'user': ['view_user', 'add_user', 'delete_user']
        },
        'auth.group': ['view_group'],
    }

```

> NOTE: to do not have the command creating a "base" group set it as ``abstract = True``


## Role inheritance
Roles can derive one-another like normal python classes, when a roles extend an other one it is not required to provide the `permissions` list. When extending an existing role its permissions gets merged with those defined in the base class.

> NOTE: ATM multi-role inheritance is not tested, it may work but it is not guaranteed.

## Database alignment
Since `Role` classes are not bound to database `Group` they must be synchronized in order to work as expected. To perform this the management command `populate_roles` is available. This command takes every configured role defined in `ROLES_MODULE` and set-up its permissions on the database, also creating the appropriate group if it does not exists yet.

See command help for further information regarding its arguments.

### Signals
Upon setup each role fires two signals:

- `pre_role_setup`: before the setup process starts, providing `role` and `clear` kwargs
- `post_role_setup`: after the setup process ends, providing `role` kwargs

## Use in unittest (TestCase)
For django style `TestCase` based testing is it possible to use the `RoleEnabledTestMixin`. This overrides the `setUpTestData` to load and create role-related data before running tests.

> NOTE: ATM it is not guaranteed that loading different roles in each test may not collide, it could be released in the future.

----


## Credits

This work was in part inspired by [django-role-permissions](https://github.com/vintasoftware/django-role-permissions).


[pypi]: https://pypi.org/project/django-group-role/
[pypi-badge]: https://img.shields.io/pypi/v/django-group-role
[pythonver]: https://img.shields.io/pypi/pyversions/django-group-role
[djversion]: https://img.shields.io/pypi/djversions/django-group-role
[ci]: https://github.com/certego/django-group-role/actions/workflows/ci.yaml
[ci-badge]: https://github.com/certego/django-group-role/actions/workflows/ci.yaml/badge.svg
