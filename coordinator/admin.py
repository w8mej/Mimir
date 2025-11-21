
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple, Dict
from mpclib.triple_pool_manager import triple_pools

app = FastAPI(title="Mimir Admin")

class Shape(BaseModel):
    A: Tuple[int, int]
    B: Tuple[int, int]
    seed: int = 0
    prefill: int = 16

@app.post("/admin/warmup")
def warmup(shapes: List[Shape]):
    created = []
    for s in shapes:
        pool = triple_pools.get_pool(tuple(s.A), tuple(s.B), seed=s.seed)
        # prefill by calling internal refill (get then immediately return to keep size)
        for _ in range(s.prefill):
            A,B,C = pool.get()
            pool.pool.append((A,B,C))  # put back to simulate prefill
        created.append({"shapeA": s.A, "shapeB": s.B, "size": len(pool.pool)})
    return {"ok": True, "pools": created}

@app.get("/admin/pools")
def pools():
    out = []
    for (A,B), pool in triple_pools.pools.items():
        out.append({"shapeA": A, "shapeB": B, "available": len(pool.pool)})
    return {"ok": True, "pools": out}
