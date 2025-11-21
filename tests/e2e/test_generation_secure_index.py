
import numpy as np
import pytest
from model.tiny_transformer import TinyTransformer2L
from model.tokenizer import ByteTokenizer

@pytest.mark.e2e
def test_e2e_generate_secure_index():
    tok = ByteTokenizer()
    model = TinyTransformer2L(d_model=32, d_ff=64, vocab_size=256, seed=123)
    prompt = "hello"
    ids = tok.encode(prompt)
    out = []
    for _ in range(4):
        nxt = model.next_token_secure_index(ids + out)
        assert 0 <= nxt < tok.vocab_size
        out.append(nxt)
    assert len(out) == 4
