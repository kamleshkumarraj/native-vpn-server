# agent/ipsec/base.py
class IPSecBase:
    def apply_tunnel(self, tunnel, policy):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError
