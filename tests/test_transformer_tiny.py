
import numpy as np
from model.tiny_transformer import TinyTransformer2L
from model.tokenizer import ByteTokenizer

def test_tiny_transformer_deterministic_step():
    tok = ByteTokenizer()
    model = TinyTransformer2L(d_model=32, d_ff=64, vocab_size=256, seed=123)
    prompt = "hello"
    ids = tok.encode(prompt)
    nxt = model.next_token_argmax(ids)
    # Deterministic given seed & prompt
    assert isinstance(nxt, int)
    assert 0 <= nxt < tok.vocab_size
