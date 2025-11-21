
import yaml, re
from dataclasses import dataclass
@dataclass
class PartyAdmission:
    kind: str
    measurement: str
def load_policy(path: str):
    """
    Load the admission policy from a YAML file.
    """
    with open(path,"r") as f: return yaml.safe_load(f)
def admit(policy, admission: PartyAdmission) -> bool:
    """
    Check if a party is admitted based on the policy.
    
    Args:
        policy: The loaded policy dict.
        admission: The party's admission evidence.
        
    Returns:
        True if admitted, False otherwise.
    """
    for rule in policy.get("admit", []):
        if rule.get("kind") != admission.kind: continue
        for m in rule.get("measurements", []):
            pref = m.get("allow_prefix")
            if pref and admission.measurement.startswith(pref):
                return True
    return False
