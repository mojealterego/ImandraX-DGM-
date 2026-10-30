"""Versioned, in-process local application boundary for future desktop/mobile shells.

No HTTP listener, Git checkout, Docker, cloud account or dynamic plugin loading.
The platform shell owns UI, app-private paths, foreground scheduling and key UI.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from threading import RLock

from .apex import ApexError, ApexRequest, ApexRuntime
from .apex_integrations import attach_unified_engine
from .engine import IntegratedEngine
from .knowledge import KnowledgeIndex

API_VERSION = 1
STATE_VERSION = 1
PLATFORMS = ('windows', 'macos', 'linux', 'android', 'ios')


@dataclass(frozen=True)
class LocalConfig:
    platform: str
    assets: Path
    state: Path
    owner_public_key: bytes | None = None


class LocalRuntime:
    """Serialized bounded calls; a shell must use one instance per state directory.

A profile declares a target, not native-platform certification. Suspension pauses
APEX, preserving identity; terminal APEX.stop is intentionally not exposed here.
"""
    def __init__(self, config: LocalConfig):
        if config.platform not in PLATFORMS:
            raise ValueError('UNSUPPORTED_PLATFORM')
        self._lock = RLock()
        assets, state = Path(config.assets).resolve(), Path(config.state).resolve()
        if assets.is_relative_to(state) or state.is_relative_to(assets):
            raise ValueError('ASSETS_AND_STATE_MUST_BE_DISJOINT')
        knowledge, inventory = assets/'mathematics.sqlite3', assets/'repositories_public_701.tsv'
        if not knowledge.is_file() or not inventory.is_file():
            raise ValueError('LOCAL_ASSETS_MISSING')
        KnowledgeIndex(knowledge).stats()  # Read-only validation before creating state.
        state.mkdir(parents=True, exist_ok=True)
        marker = state/'local-layout.json'
        expected = {'api_version': API_VERSION, 'state_version': STATE_VERSION}
        for name in ('local-layout.json', 'apex.sqlite3', 'ledger.sqlite3', 'review.sqlite3',
                     'archive.sqlite3', 'formal_proofs.sqlite3', 'research_generations.sqlite3'):
            if (state/name).is_symlink():
                raise ValueError('STATE_SYMLINK_DENIED')
        if marker.exists():
            if marker.stat().st_size > 1024 or json.loads(marker.read_text()) != expected:
                raise ValueError('STATE_MIGRATION_REQUIRED')
        else:
            # Legacy stores must be migrated explicitly, never silently adopted.
            if any(state.iterdir()):
                raise ValueError('STATE_MIGRATION_REQUIRED')
            with marker.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(expected, sort_keys=True)+'\n')
        self._engine = IntegratedEngine(knowledge_db=knowledge, inventory=inventory,
            ledger_db=state/'ledger.sqlite3', review_db=state/'review.sqlite3',
            archive_db=state/'archive.sqlite3')
        self._runtime = ApexRuntime(attach_unified_engine(self._engine), state/'apex.sqlite3',
                                    owner_public_key=config.owner_public_key)
        self._platform = config.platform

    def status(self):
        with self._lock:
            return {'api_version': API_VERSION, 'platform_target': self._platform,
                    'network_required': False, 'installers': 'DEFERRED',
                    'available_operations': ['imandrax.math', 'imandrax.formal', 'dgm.history'],
                    'unavailable_operations': ['rsi.proposals', 'release', 'deploy'],
                    'runtime': self._runtime.status()}

    def resume(self):
        with self._lock:
            if self._runtime.status()['state'] != 'ACTIVE':
                self._runtime.start()
            return self.status()

    def suspend(self):
        with self._lock:
            if self._runtime.status()['state'] == 'ACTIVE':
                self._runtime.pause()
            return self.status()

    def request(self, envelope: dict):
        """JSON-compatible contract v1; caller-generated IDs remain unique on replay."""
        with self._lock:
            if (not isinstance(envelope, dict) or
                    set(envelope) != {'api_version', 'request_id', 'operation', 'payload'} or
                    type(envelope['api_version']) is not int or envelope['api_version'] != API_VERSION):
                raise ValueError('UNSUPPORTED_REQUEST_CONTRACT')
            if envelope['operation'] not in self.status()['available_operations']:
                raise ApexError('LOCAL_CAPABILITY_UNAVAILABLE')
            return {'api_version': API_VERSION, **self._runtime.dispatch(ApexRequest(
                envelope['operation'], envelope['payload'], 'local-owner', envelope['request_id']))}
