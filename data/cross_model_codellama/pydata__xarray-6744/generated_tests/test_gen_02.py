from typing import Callable, Hashable, Any, Mapping, Iterable

import functools

import dask.array as da
import numpy as np
import pandas as pd

from xarray import DataArray, Dataset, Variable, dtypes


class Coarsen:
    def __init__(
        self,
        obj: Dataset | DataArray,
        boundary: str | Iterable[Hashable] | None = None,
        dim: Hashable | Iterable[Hashable] | None = None,
        keep_attrs: bool | None = None,
    ):
        self.obj = obj
        self.boundary = boundary
        self.dim = dim
        self.keep_attrs = keep_attrs

    def mean(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.mean, **kwargs)

    def sum(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.sum, **kwargs)

    def min(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.min, **kwargs)

    def max(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.max, **kwargs)

    def std(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.std, **kwargs)

    def var(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.var, **kwargs)

    def quantile(self, q: float | Iterable[float], **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.quantile, **kwargs)

    def argmax(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.argmax, **kwargs)

    def argmin(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.argmin, **kwargs)

    def count(self, **kwargs) -> Dataset | DataArray:
        return self._aggregate(da.count, **kwargs)

    def _aggregate(self, func: Callable, **kwargs) -> Dataset | DataArray:
        if self.dim is None:
            raise ValueError("dim must be specified.")

        if isinstance(self.dim, Hashable):
            dim = [self.dim]
        else:
            dim = self.dim

        if self.boundary is None:
            boundary = {}
        elif isinstance(self.boundary, Hashable):
            boundary = {d: self.boundary for d in dim}
        else:
            boundary = {d: b for d, b in zip(dim, self.boundary)}

        keep_attrs = self._get_keep_attrs(kwargs.pop("keep_attrs", None))

        if isinstance(self.obj, DataArray):
            if isinstance(self.obj.data, Variable):
                data = self.obj.data.data
            else:
                data = self.obj.data

            coarsened = func(data, dim=dim, boundary=boundary, keep_attrs=keep_attrs, **kwargs)
            attrs = self.obj.attrs if keep_attrs else {}
            return DataArray(coarsened, name=self.obj.name, coords=self.obj.coords, attrs=attrs)
        else:
            if isinstance(self.obj.data_vars, Mapping):
                data_vars = self.obj.data_vars
            else:
                data_vars = self.obj.data_vars.to_dict()

            new_data_vars = {}
            for name, var in data_vars.items():
                if isinstance(var.data, Variable):
                    data = var.data.data
                else:
                    data = var.data

                coarsened = func(data, dim=dim, boundary=boundary, keep_attrs=keep_attrs, **kwargs)
                attrs = var.attrs if keep_attrs else {}
                new_data_vars[name] = Variable(var.dims, coarsened, attrs)

            coords = self.obj.coords
            attrs = self.obj.attrs if keep_attrs else {}
            return Dataset(new_data_vars, coords=coords, attrs=attrs)

    def _get_keep_attrs(self, keep_attrs: bool | None = None) -> bool:
        if keep_attrs is not None:
            return keep_attrs
        elif isinstance(self.obj, DataArray):
            return self.obj.keep_attrs
        else:
            return self.obj.data_vars.keep_attrs