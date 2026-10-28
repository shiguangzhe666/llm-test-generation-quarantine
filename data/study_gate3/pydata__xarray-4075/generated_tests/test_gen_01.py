import pytest
from unittest.mock import Mock, patch
from your_module import Weighted, DataArrayWeighted, DatasetWeighted

# Mock the DataArray and Dataset for testing
class MockDataArray:
    def __init__(self, data):
        self.data = data

    def has_nans(self):
        return any(not isinstance(x, (int, float)) for x in self.data)

    def fillna(self, value):
        return MockDataArray([x if x is not None else value for x in self.data])

    def dot(self, other):
        return MockDataArray([x * y for x, y in zip(self.data, other.data)])

class MockDataset:
    def __init__(self, data):
        self.data = data

    def has_nans(self):
        return any(not isinstance(x, (int, float)) for x in self.data)

    def fillna(self, value):
        return MockDataset([x if x is not None else value for x in self.data])

    def dot(self, other):
        return MockDataset([x * y for x, y in zip(self.data, other.data)])

# ------------------------------- #
# ✅ 1. Weighted Initialization Tests
# ------------------------------- #

def test_weighted_init_with_dataarray():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    weighted = Weighted(da, weights)
    assert weighted.obj == da
    assert weighted.weights == weights

def test_weighted_init_with_dataset():
    ds = MockDataset([1, 2, 3])
    weights = MockDataset([0.5, 0.5, 0.5])
    weighted = Weighted(ds, weights)
    assert weighted.obj == ds
    assert weighted.weights == weights

def test_weighted_init_invalid_weights():
    weights = MockDataArray([None, 2, 3])
    with pytest.raises(ValueError):
        Weighted(MockDataArray([1, 2, 3]), weights)

# ------------------------------- #
# ✅ 2. _reduce Method Tests
# ------------------------------- #

def test_reduce_no_dimensions():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._reduce(da, weights, dim=None)
    assert result.data == [1 * 0.5, 2 * 0.5, 3 * 0.5]

def test_reduce_skipna_float():
    da = MockDataArray([1, None, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._reduce(da, weights, skipna=True)
    assert result.data == [0.5, 0.0, 1.5]

def test_reduce_skipna_int():
    da = MockDataArray([1, None, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    with pytest.raises(ValueError):
        Weighted._reduce(da, weights, skipna=False)

def test_reduce_calls_dot():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    with patch('your_module.dot') as mock_dot:
        Weighted._reduce(da, weights, skipna=False)
        mock_dot.assert_called_once_with(da, weights)

# ------------------------------- #
# ✅ 3. _sum_of_weights Method Tests
# ------------------------------- #

def test_sum_of_weights_masks_nans():
    da = MockDataArray([1, None, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._sum_of_weights(da, weights)
    assert result.data == [0.5, 0.0, 1.5]

def test_sum_of_weights_zero_sum():
    da = MockDataArray([0, 0, 0])
    weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._sum_of_weights(da, weights)
    assert result.data == [0.0, 0.0, 0.0]

def test_sum_of_weights_returns_zero_when_sum_is_zero():
    da = MockDataArray([0, 0, 0])
    weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._sum_of_weights(da, weights)
    assert result.data == [0.0, 0.0, 0.0]

# ------------------------------- #
# ✅ 4. _weighted_sum and _weighted_mean Tests
# ------------------------------- #

def test_weighted_sum_calls_reduce():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    with patch('your_module._reduce') as mock_reduce:
        Weighted._weighted_sum(da, weights)
        mock_reduce.assert_called_once_with(da, weights, skipna=False)

def test_weighted_mean_calls_sum_and_weighted_sum():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    with patch('your_module._sum_of_weights') as mock_sum, patch('your_module._weighted_sum') as mock_weighted_sum:
        Weighted._weighted_mean(da, weights)
        mock_sum.assert_called_once_with(da, weights)
        mock_weighted_sum.assert_called_once_with(da, weights)

def test_weighted_mean_divides_by_sum():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.5, 0.5, 0.5])
    weighted_sum = MockDataArray([0.5, 1.0, 1.5])
    sum_of_weights = MockDataArray([0.5, 0.5, 0.5])
    result = Weighted._weighted_mean(da, weights)
    assert result.data == [1.0, 2.0, 3.0]

def test_weighted_mean_returns_zero_on_zero_sum():
    da = MockDataArray([1, 2, 3])
    weights = MockDataArray([0.0, 0.0, 0.0])
    result = Weighted._weighted_mean(da, weights)
    assert result.data == [0.0, 0.0, 0.0]

# ------------------------------- #
#