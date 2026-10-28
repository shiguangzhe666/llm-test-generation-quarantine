import pytest
import numpy as np
from xarray.core.nanops import nanmin, nanmax, nanargmin, nanargmax, nansum, nanmean, nanmedian, nanvar, nanstd, nanprod, nancumsum, nancumprod

def test_nanmin():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanmin(data) == 1

def test_nanmax():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanmax(data) == 10

def test_nanargmin():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanargmin(data) == 0

def test_nanargmax():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanargmax(data) == 9

def test_nansum():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nansum(data) == 55

def test_nanmean():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanmean(data) == 5.5

def test_nanmedian():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanmedian(data) == 5.5

def test_nanvar():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanvar(data) == 35.25

def test_nanstd():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanstd(data) == 5.5 * np.sqrt(10)

def test_nanprod():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nanprod(data) == 3628800

def test_nancumsum():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nancumsum(data) == np.array([1, 3, 6, 10, 15, 21, 28, 36, 45, 55])

def test_nancumprod():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert nancumprod(data) == np.array([1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3276720])