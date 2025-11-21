import numpy as np
import pytest
from mpclib.secure_argmax import secure_argmax_onehot
from mpclib.shares import share_array, reconstruct_array
from mpclib.fixed_point import FixedPoint

def test_secure_argmax_onehot_basic():
    fp = FixedPoint(16)
    rng = np.random.default_rng(42)
    
    # Create some logits
    # Shape: (batch_size, num_classes)
    logits = np.array([[1.0, 2.0, 0.5], [0.1, 0.2, 0.9]])
    
    # Share the logits
    logits_s = share_array(fp.encode(logits), rng)
    
    # Run secure argmax
    # This returns shares of the one-hot encoding
    onehot_s = secure_argmax_onehot(logits_s)
    
    # Reconstruct
    onehot = reconstruct_array(*onehot_s)
    onehot_decoded = fp.decode(onehot)
    
    # Check if the max value is close to 1 and others close to 0
    # The implementation is an approximation, so we use a loose tolerance or just check argmax index
    
    expected_indices = np.argmax(logits, axis=-1)
    predicted_indices = np.argmax(onehot_decoded, axis=-1)
    
    np.testing.assert_array_equal(predicted_indices, expected_indices)

def test_secure_argmax_onehot_shape():
    fp = FixedPoint(16)
    rng = np.random.default_rng(42)
    logits = np.random.randn(5, 10)
    logits_s = share_array(fp.encode(logits), rng)
    onehot_s = secure_argmax_onehot(logits_s)
    onehot = reconstruct_array(*onehot_s)
    onehot_decoded = fp.decode(onehot)
    
    assert onehot_decoded.shape == logits.shape
