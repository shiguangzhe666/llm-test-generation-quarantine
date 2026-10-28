import numpy as np
import pytest
from unittest.mock import patch
from xarray.core import nanops

def test_replace_nan():
    a = np.array([1, np.nan, 3, np.nan, 5])
    val = 999
    result, mask = nanops._replace_nan(a, val)
    assert np.array_equal(result, np.array([1, 999, 3, 999, 5]))
    assert np.array_equal(mask, np.array([False, True, False, True, False]))

def test_maybe_null_out():
    result = np.array([1, 2, 3, 4, 5])
    mask = np.array([False, False, False, False, False])
    axis = 0
    min_count = 1
    assert np.array_equal(nanops._maybe_null_out(result, axis, mask, min_count), result)

    min_count = 6
    assert np.array_equal(nanops._maybe_null_out(result, axis, mask, min_count), np.nan)

    result = np.array([[1, 2, 3], [4, 5, np.nan]])
    mask = np.array([[False, False, False], [False, False, True]])
    axis = 1
    min_count = 1
    assert np.array_equal(nanops._maybe_null_out(result, axis, mask, min_count), np.array([[1, 2, 3], [4, 5, 3]]))

    axis = 0
    min_count = 2
    assert np.array_equal(nanops._maybe_null_out(result, axis, mask, min_count), np.array([[1, 2, 3], [4, 5, 3]]))

def test_nan_minmax_object():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops._nan_minmax_object("min", np.inf, a) == 1
    assert nanops._nan_minmax_object("max", -np.inf, a) == 5

    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops._nan_minmax_object("min", np.inf, a) == 1
    assert nanops._nan_minmax_object("max", -np.inf, a) == "5"

def test_nanargmin_nanargmax():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops._nan_argminmax_object("argmin", np.inf, a) == 0
    assert nanops._nan_argminmax_object("argmax", -np.inf, a) == 4

    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops._nan_argminmax_object("argmin", np.inf, a) == 0
    assert nanops._nan_argminmax_object("argmax", -np.inf, a) == 4

def test_nansum():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nansum(a) == 12
    assert nanops.nansum(a, min_count=3) == 12
    assert nanops.nansum(a, min_count=5) == np.nan

def test_nanmean():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nanmean(a) == 2.2
    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops.nanmean(a) == 2.2

def test_nanmedian():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nanmedian(a) == 2.5
    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops.nanmedian(a) == 3

def test_nanvar():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nanvar(a) == 2.2
    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops.nanvar(a) == 2.2

def test_nanstd():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nanstd(a) == np.sqrt(2.2)
    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops.nanstd(a) == np.sqrt(2.2)

def test_nanprod():
    a = np.array([1, 2, np.nan, 4, 5])
    assert nanops.nanprod(a) == 80
    a = np.array([1, "2", np.nan, 4, "5"])
    assert nanops.nanprod(a) == 80

def test_nancumsum():
    a = np.array([1, 2, np.nan, 4, 5])
    assert np.array_equal(nanops.nancumsum(a), np.array([1, 3, 3, 7, 12]))
    a = np.array([1, "2", np.nan, 4, "5"])
    assert np.array_equal(nanops.nancumsum(a), np.array([1, 3, 3, 7, 12]))

def test_nancumprod():
    a = np.array([1, 2, np.nan, 4, 5])
    assert np.array_equal(nanops.nancumprod(a), np.array([1, 2, 2, 8, 40]))
    a = np.array([1, "2", np.nan, 4, "5"])
    assert np.array_equal(nanops.nancumprod(a), np.array([1, 2, 2, 8, 40]))