

def merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    if merge_dct is None:
        return dct

    for k, v in merge_dct.items():
        if k not in dct:
            dct[k] = merge_dct[k]
        else:
            if isinstance(dct[k], dict):
                dct[k] = merge(dct[k], merge_dct[k])
            elif isinstance(dct[k], list):
                dct[k] = dct[k] + merge_dct[k]
            else:
                dct[k] = merge_dct[k]

    return dct