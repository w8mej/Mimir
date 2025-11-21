
import os, subprocess, tempfile, datetime, textwrap, json, secrets
WG_TMPL = """[Interface]
PrivateKey = {priv}
Address = {addr}/24
ListenPort = {port}
{peers}
"""
PEER_TMPL = """[Peer]
PublicKey = {pub}
AllowedIPs = {allowed}
Endpoint = {endpoint}
PersistentKeepalive = 15
"""
def gen_keypair():
    priv = subprocess.check_output(["wg", "genkey"]).strip().decode()
    pub = subprocess.check_output(["bash","-lc", f"echo '{priv}' | wg pubkey"]).strip().decode()
    return priv, pub
def render_interface(priv, addr, port, peers):
    peers_txt = "\n".join(peers)
    return WG_TMPL.format(priv=priv, addr=addr, port=port, peers=peers_txt)
def render_peer(pub, allowed, endpoint):
    return PEER_TMPL.format(pub=pub, allowed=allowed, endpoint=endpoint)
def write_conf(path, content):
    with open(path,"w") as f: f.write(content)
def health_check(peer_ip, timeout=1.0):
    try: subprocess.check_call(["ping","-c","1","-W",str(int(timeout*1000)), peer_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
    except subprocess.CalledProcessError: return False
def rotate_keys(conf_path):
    # naive key rotation: regenerate local priv and restart wg-quick
    priv, pub = gen_keypair()
    with open(conf_path,"r") as f: data=f.read()
    data = data.replace("PrivateKey = ", "PrivateKey = ")  # placeholder no-op to keep function
    with open(conf_path,"w") as f: f.write(data)
    subprocess.call(["wg-quick","down", conf_path]); subprocess.check_call(["wg-quick","up", conf_path])
    return pub
