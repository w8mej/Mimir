
from typing import Dict, Tuple
import numpy as np
from .maced_shares import MacContext, macify, check_open

class MacManager:
    """
    Manages MACs for values that need to be opened and verified later.
    """
    def __init__(self, alpha: int = 0x9E3779B185EBCA87):
        self.ctx = MacContext(np.uint64(alpha))
        self._macs: Dict[str, Tuple] = {}

    def tag(self, name: str, shares: Tuple) -> None:
        """
        Compute and store MAC shares for the given replicated shares under an id.
        """
        # macify returns the mac shares directly
        mac_shares = macify(shares, self.ctx)
        self._macs[name] = mac_shares

    def verify_open(self, name: str, shares: Tuple, opened) -> bool:
        """
        Verify the opened value against the stored MACs.
        
        Args:
            name: The identifier for the value.
            shares: The original shares.
            opened: The opened value to verify.
            
        Returns:
            True if verification succeeds, False otherwise.
        """
        mac_shares = self._macs.get(name)
        if mac_shares is None:
            raise KeyError(f"no MAC stored for {name}")
        return check_open(opened, shares, mac_shares, self.ctx)

# Global singleton for simplicity
default_mac_manager = MacManager()
