import sys
from unittest.mock import MagicMock, patch
import pytest

# Create dummy modules for protobufs
class DummyMessage:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __repr__(self):
        return f"DummyMessage({self.__dict__})"

class DummyPB:
    def RegisterAck(self, **kwargs): return DummyMessage(**kwargs)
    def SessionAck(self, **kwargs): return DummyMessage(**kwargs)
    def SubmitPromptAck(self, **kwargs): return DummyMessage(**kwargs)
    def Metrics(self, **kwargs): return DummyMessage(**kwargs)
    def Token(self, **kwargs): return DummyMessage(**kwargs)
    def InferenceEvent(self, **kwargs): return DummyMessage(**kwargs)
    def StepTiming(self, **kwargs): return DummyMessage(**kwargs)

class DummyGRPC:
    class CoordinatorServicer:
        pass
    def add_CoordinatorServicer_to_server(self, *args): pass

# Setup mocks
module_mock = MagicMock()
pb_mock = DummyPB()
grpc_mock = DummyGRPC()

# Link attributes so that 'from coordinator.pb import ...' works via attribute access on parent
module_mock.coordinator_pb2 = pb_mock
module_mock.coordinator_pb2_grpc = grpc_mock

# We use patch.dict to ensure we are patching sys.modules correctly
@pytest.fixture(scope="module", autouse=True)
def setup_mocks():
    with patch.dict(sys.modules, {
        'coordinator.pb': module_mock,
        'coordinator.pb.coordinator_pb2': pb_mock,
        'coordinator.pb.coordinator_pb2_grpc': grpc_mock,
        'grpc': MagicMock(),
        'model.tiny_transformer': MagicMock(),
        'model.tokenizer': MagicMock(),
    }):
        yield

def test_register_party():
    """
    Test party registration flow.
    """
    with patch('coordinator.policy.load_policy'), \
         patch('coordinator.grpc_server.ensure_proto'):
        
        # Import inside the patched environment
        from coordinator.grpc_server import CoordinatorService
        import coordinator.grpc_server as grpc_server
        
        print(f"DEBUG: grpc_server.pb type: {type(grpc_server.pb)}")
        print(f"DEBUG: grpc_server.pb value: {grpc_server.pb}")
        
        service = CoordinatorService()
        req = MagicMock(party_id="p1")
        resp = service.RegisterParty(req, None)
        
        print(f"DEBUG: resp type: {type(resp)}")
        print(f"DEBUG: resp value: {resp}")
        
        assert resp.ok
        assert "Registered p1" in resp.msg

def test_create_session():
    """
    Test session creation flow.
    """
    with patch('coordinator.policy.load_policy'), \
         patch('coordinator.grpc_server.ensure_proto'):
        from coordinator.grpc_server import CoordinatorService
        service = CoordinatorService()
        resp = service.CreateSession(None, None)
        assert resp.ok
        assert resp.msg == "session created"

def test_submit_prompt():
    """
    Test prompt submission flow.
    """
    with patch('coordinator.policy.load_policy'), \
         patch('coordinator.grpc_server.ensure_proto'):
        from coordinator.grpc_server import CoordinatorService
        service = CoordinatorService()
        resp = service.SubmitPrompt(None, None)
        assert resp.ok
        assert resp.msg == "prompt accepted"

def test_fetch_metrics():
    """
    Test metrics fetching.
    """
    with patch('coordinator.policy.load_policy'), \
         patch('coordinator.grpc_server.ensure_proto'):
        from coordinator.grpc_server import CoordinatorService
        service = CoordinatorService()
        resp = service.FetchMetrics(None, None)
        assert resp.tokens_per_second == 0.0
        assert resp.triple_pool_remaining == 0

def test_run_inference():
    """
    Test inference execution flow.
    """
    with patch('coordinator.policy.load_policy'), \
         patch('coordinator.grpc_server.ensure_proto'), \
         patch('coordinator.grpc_server.model') as mock_model, \
         patch('coordinator.grpc_server.tok') as mock_tok:
        
        from coordinator.grpc_server import CoordinatorService
        
        mock_model.next_token_secure_index.return_value = 123
        mock_tok.decode.return_value = "test"
        
        service = CoordinatorService()
        req = MagicMock(max_new_tokens=2)
        iterator = service.RunInference(req, None)
        events = list(iterator)
        
        assert len(events) == 4
        assert events[0].token.token_id == 123
        assert events[0].token.text == "test"
