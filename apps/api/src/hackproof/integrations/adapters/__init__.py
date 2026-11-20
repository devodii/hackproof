from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.adapters.reflector import ReflectorAdapter
from hackproof.integrations.adapters.trustless_work import TrustlessWorkAdapter

ADAPTERS: dict[str, Adapter] = {
    adapter.name: adapter for adapter in (ReflectorAdapter(), TrustlessWorkAdapter())
}
