
import argparse
import numpy as np
import grpc
import mimir_pb2 as pb
import mimir_pb2_grpc as pb_grpc
from model.tokenizer import ByteTokenizer

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--addr", default="localhost:8080")
    ap.add_argument("--prompt", default="Hello MPC")
    ap.add_argument("--session-id", default="demo")
    ap.add_argument("--max-new-tokens", type=int, default=16)
    args = ap.parse_args()

    ch = grpc.insecure_channel(args.addr)
    stub = pb_grpc.CoordinatorStub(ch)

    tok = ByteTokenizer()
    ids = tok.encode(args.prompt)
    arr = np.array(ids, dtype=np.int64)

    stub.RegisterParty(pb.PartyInfo(party_id="party0", addr="localhost:7000"))
    stub.CreateSession(pb.SessionSpec(session_id=args.session_id, model_name="tiny", mpc_ring="2^64"))
    stub.SubmitPrompt(pb.SubmitPromptReq(session_id=args.session_id, owner_party="party0", token_ids=arr.tobytes()))

    print(f"→ prompt: {args.prompt!r}")
    out = []
    for ev in stub.RunInference(pb.RunInferenceReq(session_id=args.session_id, max_new_tokens=args.max_new_tokens, temperature=1.0, top_k=1)):
        which = ev.WhichOneof("evt")
        if which == "token":
            out.append(ev.token.token_id)
            print("TOKEN:", ev.token.token_id, repr(ev.token.text))
        elif which == "timing":
            print("STEP:", ev.timing.step_index, f"{ev.timing.ms:.2f} ms")
    print("→ decoded:", tok.decode(out))

if __name__ == "__main__":
    main()
