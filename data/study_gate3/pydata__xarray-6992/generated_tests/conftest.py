# NumPy 2.0 compatibility shim for old xarray versions
import numpy as np
if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_
if not hasattr(np, 'bool'):
    pass  # np.bool was removed in NumPy 1.24+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
