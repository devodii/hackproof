from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.adapters.reflector import ReflectorAdapter

ADAPTERS: dict[str, Adapter] = {
    adapter.name: adapter for adapter in (ReflectorAdapter(),)
}
