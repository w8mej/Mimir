
class ByteTokenizer:
    def __init__(self): self.vocab_size = 256
    def encode(self, s: str): return [c for c in s.encode("utf-8")]
    def decode(self, ids): return bytes([i%256 for i in ids]).decode("utf-8", errors="ignore")
