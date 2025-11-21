
import streamlit as st
import numpy as np
import grpc
import mimir_pb2 as pb
import mimir_pb2_grpc as pb_grpc
from model.tokenizer import ByteTokenizer

st.set_page_config(page_title="Mimir Demo", layout="centered")

st.title("Mimir • Confidential AR Inference (Demo)")
addr = st.text_input("Coordinator address", "localhost:8080")
session_id = st.text_input("Session ID", "demo")
prompt = st.text_area("Prompt", "Hello MPC", height=100)
max_new = st.slider("Max new tokens", 1, 64, 16)

if st.button("Generate"):
    tok = ByteTokenizer()
    ids = tok.encode(prompt)
    arr = np.array(ids, dtype=np.int64)

    ch = grpc.insecure_channel(addr)
    stub = pb_grpc.CoordinatorStub(ch)

    stub.RegisterParty(pb.PartyInfo(party_id="party0", addr="localhost:7000"))
    stub.CreateSession(pb.SessionSpec(session_id=session_id, model_name="tiny", mpc_ring="2^64"))
    stub.SubmitPrompt(pb.SubmitPromptReq(session_id=session_id, owner_party="party0", token_ids=arr.tobytes()))

    out_tokens = []
    out_text = ""
    placeholder = st.empty()
    for ev in stub.RunInference(pb.RunInferenceReq(session_id=session_id, max_new_tokens=max_new, temperature=1.0, top_k=1)):
        which = ev.WhichOneof("evt")
        if which == "token":
            out_tokens.append(ev.token.token_id)
            out_text += ev.token.text
            placeholder.markdown(f"**Streaming output:** `{out_text}`")
        elif which == "timing":
            st.caption(f"Step latency: {ev.timing.ms:.2f} ms")

    st.success("Done")
    st.code(f"Decoded: {tok.decode(out_tokens)}", language="text")
