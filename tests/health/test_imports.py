
import importlib
import pytest

@pytest.mark.health
def test_imports():
    modules = [
        "mpclib.fixed_point",
        "mpclib.shares",
        "mpclib.triples",
        "mpclib.triple_pool",
        "mpclib.triple_pool_manager",
        "mpclib.secure_softmax",
        "mpclib.secure_argmax",
        "mpclib.open_with_mac",
        "mpclib.mac_manager",
        "coordinator.app",
        "coordinator.scheduler",
        "model.tiny_transformer",
        "model.tokenizer",
    ]
    for m in modules:
        importlib.import_module(m)
