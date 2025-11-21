
# WireGuard (optional)

Place your WireGuard configs here (e.g., `wg0.conf`) and bring up the interface
before starting the coordinator so the MPC nodes communicate over the secure overlay.

Example:
```bash
sudo wg-quick up docker/wireguard/wg0.conf
```
