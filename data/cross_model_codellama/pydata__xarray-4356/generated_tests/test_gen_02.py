import numpy as np
from xarray.core.nanops import (
    nanmin,
    nanmax,
    nanargmin,
    nanargmax,
    nansum,
    nanmean,
    nanmedian,
    nanvar,
    nanstd,
    nanprod,
    nancumsum,
    nancumprod,
)


def test_nanmin():
    assert nanmin(np.array([1, 2, 3, 4, 5])) == 1
    assert nanmin(np.array([1, 2, 3, 4, 5, np.nan])) == 1
    assert nanmin(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanmin(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanmax():
    assert nanmax(np.array([1, 2, 3, 4, 5])) == 5
    assert nanmax(np.array([1, 2, 3, 4, 5, np.nan])) == 5
    assert nanmax(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanmax(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanargmin():
    assert nanargmin(np.array([1, 2, 3, 4, 5])) == 0
    assert nanargmin(np.array([1, 2, 3, 4, 5, np.nan])) == 0
    assert nanargmin(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanargmin(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanargmax():
    assert nanargmax(np.array([1, 2, 3, 4, 5])) == 4
    assert nanargmax(np.array([1, 2, 3, 4, 5, np.nan])) == 4
    assert nanargmax(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanargmax(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nansum():
    assert nansum(np.array([1, 2, 3, 4, 5])) == 15
    assert nansum(np.array([1, 2, 3, 4, 5, np.nan])) == 15
    assert nansum(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nansum(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanmean():
    assert nanmean(np.array([1, 2, 3, 4, 5])) == 3
    assert nanmean(np.array([1, 2, 3, 4, 5, np.nan])) == 3
    assert nanmean(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanmean(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanmedian():
    assert nanmedian(np.array([1, 2, 3, 4, 5])) == 3
    assert nanmedian(np.array([1, 2, 3, 4, 5, np.nan])) == 3
    assert nanmedian(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanmedian(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanvar():
    assert nanvar(np.array([1, 2, 3, 4, 5])) == 2
    assert nanvar(np.array([1, 2, 3, 4, 5, np.nan])) == 2
    assert nanvar(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanvar(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanstd():
    assert nanstd(np.array([1, 2, 3, 4, 5])) == np.sqrt(2)
    assert nanstd(np.array([1, 2, 3, 4, 5, np.nan])) == np.sqrt(2)
    assert nanstd(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanstd(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nanprod():
    assert nanprod(np.array([1, 2, 3, 4, 5])) == 120
    assert nanprod(np.array([1, 2, 3, 4, 5, np.nan])) == 120
    assert nanprod(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nanprod(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nancumsum():
    assert nancumsum(np.array([1, 2, 3, 4, 5])) == [1, 3, 6, 10, 15]
    assert nancumsum(np.array([1, 2, 3, 4, 5, np.nan])) == [1, 3, 6, 10, 15]
    assert nancumsum(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nancumsum(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)


def test_nancumprod():
    assert nancumprod(np.array([1, 2, 3, 4, 5])) == [1, 2, 6, 24, 120]
    assert nancumprod(np.array([1, 2, 3, 4, 5, np.nan])) == [1, 2, 6, 24, 120]
    assert nancumprod(np.array([1, 2, 3, 4, 5, np.nan]), axis=0).shape == (5,)
    assert nancumprod(np.array([1, 2, 3, 4, 5, np.nan]), axis=1).shape == (5,)