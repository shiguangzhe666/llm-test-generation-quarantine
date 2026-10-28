import pytest
from xarray.core.weighted import Weighted


def test_sum_of_weights():
    data = Weighted(None, None)
    assert data.sum_of_weights().equals(data.obj.sum(dim='weights'))


def test_sum():
    data = Weighted(None, None)
    assert data.sum().equals(data.obj.sum(dim='weights'))


def test_mean():
    data = Weighted(None, None)
    assert data.mean().equals(data.obj.mean(dim='weights'))


def test_repr():
    data = Weighted(None, None)
    assert repr(data) == 'Weighted with weights along dimensions: weights'


def test_not_implemented():
    with pytest.raises(NotImplementedError):
        Weighted(None, None)._implementation(None, None, None)