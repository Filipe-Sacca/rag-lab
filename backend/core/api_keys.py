"""
API Key Rotation Manager

Manages multiple Google API keys from different projects to distribute
rate limit load. Quota is per-project, so multiple projects = multiple quotas.

Features:
- Round-robin rotation
- Automatic retry on 429 errors with next key
- Key health tracking (marks exhausted keys temporarily)
- Thread-safe for async usage
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class APIKeyStatus:
    """Track status of individual API key."""
    key: str
    project_name: str
    is_exhausted: bool = False
    exhausted_until: float = 0.0
    request_count: int = 0
    error_count: int = 0
    last_used: float = field(default_factory=time.time)

    def mark_exhausted(self, cooldown_seconds: float = 60.0) -> None:
        """Mark key as exhausted for cooldown period."""
        self.is_exhausted = True
        self.exhausted_until = time.time() + cooldown_seconds
        self.error_count += 1
        logger.warning(
            f"API key [{self.project_name}] exhausted. "
            f"Cooling down for {cooldown_seconds}s"
        )

    def is_available(self) -> bool:
        """Check if key is available for use."""
        if not self.is_exhausted:
            return True
        if time.time() > self.exhausted_until:
            self.is_exhausted = False
            logger.info(f"API key [{self.project_name}] recovered from cooldown")
            return True
        return False

    def record_success(self) -> None:
        """Record successful request."""
        self.request_count += 1
        self.last_used = time.time()


class APIKeyRotator:
    """
    Manages rotation of multiple API keys across different projects.

    Usage:
        rotator = APIKeyRotator()
        rotator.add_key("key1", "project-a")
        rotator.add_key("key2", "project-b")

        key = rotator.get_next_key()
        # Use key for API call
        # On 429 error:
        rotator.mark_current_exhausted(cooldown=60)
    """

    def __init__(self):
        self._keys: list[APIKeyStatus] = []
        self._current_index: int = 0
        self._lock = asyncio.Lock()

    def add_key(self, api_key: str, project_name: str = "unknown") -> None:
        """Add an API key to the rotation pool."""
        # Avoid duplicates
        for existing in self._keys:
            if existing.key == api_key:
                logger.debug(f"Key for [{project_name}] already exists, skipping")
                return

        self._keys.append(APIKeyStatus(key=api_key, project_name=project_name))
        logger.info(f"Added API key for project [{project_name}]. Total keys: {len(self._keys)}")

    def add_keys_from_string(self, keys_string: str) -> None:
        """
        Add multiple keys from comma-separated string.

        Format: "key1,key2,key3" or "key1:project1,key2:project2"
        """
        if not keys_string:
            return

        for i, item in enumerate(keys_string.split(",")):
            item = item.strip()
            if not item:
                continue

            if ":" in item:
                key, project = item.split(":", 1)
                self.add_key(key.strip(), project.strip())
            else:
                self.add_key(item, f"project-{i+1}")

    @property
    def total_keys(self) -> int:
        """Total number of keys in rotation."""
        return len(self._keys)

    @property
    def available_keys(self) -> int:
        """Number of keys currently available."""
        return sum(1 for k in self._keys if k.is_available())

    def get_next_key(self) -> Optional[str]:
        """
        Get next available API key using round-robin.

        Returns None if all keys are exhausted.
        """
        if not self._keys:
            logger.error("No API keys configured!")
            return None

        # Try each key once
        for _ in range(len(self._keys)):
            key_status = self._keys[self._current_index]
            self._current_index = (self._current_index + 1) % len(self._keys)

            if key_status.is_available():
                logger.debug(
                    f"Using API key [{key_status.project_name}] "
                    f"(requests: {key_status.request_count})"
                )
                return key_status.key

        # All keys exhausted
        logger.error("All API keys are exhausted!")
        return None

    def get_current_key(self) -> Optional[str]:
        """Get current key without rotating."""
        if not self._keys:
            return None
        idx = (self._current_index - 1) % len(self._keys)
        return self._keys[idx].key

    def mark_key_exhausted(
        self,
        api_key: str,
        cooldown_seconds: float = 60.0
    ) -> None:
        """Mark specific key as exhausted."""
        for key_status in self._keys:
            if key_status.key == api_key:
                key_status.mark_exhausted(cooldown_seconds)
                return

    def mark_current_exhausted(self, cooldown_seconds: float = 60.0) -> None:
        """Mark the most recently used key as exhausted."""
        if not self._keys:
            return
        idx = (self._current_index - 1) % len(self._keys)
        self._keys[idx].mark_exhausted(cooldown_seconds)

    def record_success(self, api_key: str) -> None:
        """Record successful request for a key."""
        for key_status in self._keys:
            if key_status.key == api_key:
                key_status.record_success()
                return

    def get_stats(self) -> dict:
        """Get statistics about all keys."""
        return {
            "total_keys": self.total_keys,
            "available_keys": self.available_keys,
            "keys": [
                {
                    "project": k.project_name,
                    "requests": k.request_count,
                    "errors": k.error_count,
                    "is_available": k.is_available(),
                    "is_exhausted": k.is_exhausted,
                }
                for k in self._keys
            ]
        }

    def get_all_keys(self) -> list[str]:
        """Get all API keys (for batch operations)."""
        return [k.key for k in self._keys]


# Global singleton instance
_rotator: Optional[APIKeyRotator] = None


def get_api_key_rotator() -> APIKeyRotator:
    """Get or create the global API key rotator instance."""
    global _rotator
    if _rotator is None:
        _rotator = APIKeyRotator()
    return _rotator


def initialize_rotator(
    primary_key: str,
    additional_keys: str = "",
) -> APIKeyRotator:
    """
    Initialize the API key rotator with keys.

    Args:
        primary_key: Main API key (from GOOGLE_API_KEY)
        additional_keys: Comma-separated additional keys (from GOOGLE_API_KEYS)

    Returns:
        Configured APIKeyRotator instance
    """
    rotator = get_api_key_rotator()

    # Add primary key first
    if primary_key:
        rotator.add_key(primary_key, "primary")

    # Add additional keys
    if additional_keys:
        rotator.add_keys_from_string(additional_keys)

    logger.info(f"API Key Rotator initialized with {rotator.total_keys} keys")
    return rotator
