
import hashlib

class Transcript:
    def __init__(self):
        self._h = hashlib.sha256()

    def append(self, *parts: bytes):
        for p in parts:
            self._h.update(p if isinstance(p, (bytes, bytearray)) else str(p).encode())

    @property
    def digest(self) -> bytes:
        return self._h.digest()
