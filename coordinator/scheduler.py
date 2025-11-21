
import time
import numpy as np
from prometheus_client import Counter, Histogram

from model.tiny_transformer import TinyTransformer2L
from model.tokenizer import ByteTokenizer

GEN_TOKENS = Counter("mimir_generated_tokens_total", "Total tokens generated")
GEN_STEPS = Counter("mimir_generation_steps_total", "Total generation steps")
STEP_LAT = Histogram("mimir_step_latency_seconds", "Latency per generated token")

class AutoRegScheduler:
    def __init__(self):
        self.models = {}
        self.toks = {}
        self.prompts = {}

    def ensure_session(self, session_id):
        if session_id not in self.models:
            self.models[session_id] = TinyTransformer2L(d_model=32, d_ff=64, vocab_size=256, seed=123)
            self.toks[session_id] = ByteTokenizer()

    def load_prompt_bytes(self, session_id, token_bytes):
        arr = np.frombuffer(token_bytes, dtype=np.int64)
        ids = [int(x) for x in arr.tolist()]
        self.prompts[session_id] = ids

    def run(self, session_id, max_new_tokens, topk=3):
        self.ensure_session(session_id)
        model = self.models[session_id]
        tok = self.toks[session_id]
        ids = list(self.prompts.get(session_id, []))
        seed = len(ids)  # simple deterministic seed per session

        for step in range(max_new_tokens):
            t0 = time.perf_counter()
            nxt = model.next_token_topk(ids, k=topk, seed=seed + step)
            ids.append(nxt)
            dt = time.perf_counter() - t0
            GEN_TOKENS.inc(); GEN_STEPS.inc(); STEP_LAT.observe(dt)
            text = tok.decode([nxt])
            yield nxt, text, dt
