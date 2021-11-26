from collections import defaultdict
from functools import reduce


def _map_permissions(perm_map, permissions):
    if not permissions:
        return perm_map

    assert isinstance(
        permissions, (list, tuple, set, dict)
    ), "Role permissions must be a list, a set, a tuple or a dict"
    if isinstance(permissions, dict):
        # keys are app_label or app_label.model
        for label, perms in permissions.items():
            try:
                app_label, modelname = label.split(".", 1)
            except ValueError:
                app_label = label
                if not isinstance(perms, dict):
                    raise ValueError(
                        "App permissions must be provided on per-model bases by providing a dict"
                    )
                for modelname, model_perms in perms.items():
                    perm_map[app_label][modelname] |= set(model_perms)
            else:
                perm_map[app_label][modelname] |= set(perms)
    else:
        # legacy permission definition
        for perm in permissions:
            try:
                app_label, codename = perm.split(".", 1)
            except ValueError:
                raise ValueError(
                    "Permissions, should be defined in the"
                    f" format: 'app_label.codename' (is {perm})"
                )
            perm_map[app_label]["_codenames"].add(codename)

    return perm_map


def map_permissions(*permissions_list):
    perm_map = defaultdict(lambda: defaultdict(set))
    return reduce(_map_permissions, permissions_list, perm_map)
