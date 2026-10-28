"""
Cache manager module - designed to trigger common flakiness patterns in LLM-generated tests.
Contains file I/O, timing, caching with TTL, and concurrent access patterns.
"""
import os
import json
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta


class CacheEntry:
    """A single cache entry with TTL support."""
    
    def __init__(self, key, value, ttl_seconds=300):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = self.created_at
    
    @property
    def is_expired(self):
        return time.time() - self.created_at > self.ttl_seconds
    
    @property
    def age_seconds(self):
        return time.time() - self.created_at
    
    def touch(self):
        self.last_accessed = time.time()
        self.access_count += 1


class SimpleCache:
    """Thread-safe in-memory cache with TTL and file persistence."""
    
    def __init__(self, max_size=100, default_ttl=300):
        self._store = {}
        self._lock = threading.Lock()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get(self, key, default=None):
        """Get a value from cache."""
        with self._lock:
            if key in self._store:
                entry = self._store[key]
                if entry.is_expired:
                    del self._store[key]
                    self.stats["misses"] += 1
                    return default
                entry.touch()
                self.stats["hits"] += 1
                return entry.value
            self.stats["misses"] += 1
            return default
    
    def set(self, key, value, ttl=None):
        """Set a value in cache."""
        ttl = ttl if ttl is not None else self.default_ttl
        with self._lock:
            if len(self._store) >= self.max_size and key not in self._store:
                self._evict_one()
            self._store[key] = CacheEntry(key, value, ttl)
    
    def delete(self, key):
        """Delete a key from cache."""
        with self._lock:
            return self._store.pop(key, None) is not None
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            self._store.clear()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def keys(self):
        """Return non-expired keys."""
        with self._lock:
            return [k for k, v in self._store.items() if not v.is_expired]
    
    @property
    def size(self):
        return len(self._store)
    
    @property
    def hit_rate(self):
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0.0
    
    def _evict_one(self):
        """Evict the least recently accessed entry."""
        if not self._store:
            return
        oldest_key = min(self._store, key=lambda k: self._store[k].last_accessed)
        del self._store[oldest_key]
        self.stats["evictions"] += 1
    
    def save_to_file(self, filepath):
        """Persist cache to a JSON file."""
        data = {}
        with self._lock:
            for key, entry in self._store.items():
                if not entry.is_expired:
                    data[key] = {
                        "value": entry.value,
                        "created_at": entry.created_at,
                        "ttl": entry.ttl_seconds,
                    }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return len(data)
    
    def load_from_file(self, filepath):
        """Load cache from a JSON file."""
        if not os.path.exists(filepath):
            return 0
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for key, info in data.items():
            remaining_ttl = info["ttl"] - (time.time() - info["created_at"])
            if remaining_ttl > 0:
                self.set(key, info["value"], ttl=remaining_ttl)
                count += 1
        return count


def compute_hash(data, algorithm="sha256"):
    """Compute hash of arbitrary data."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    elif not isinstance(data, bytes):
        data = json.dumps(data, sort_keys=True).encode("utf-8")
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def format_timestamp(ts=None, fmt="%Y-%m-%d %H:%M:%S"):
    """Format a Unix timestamp or current time."""
    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts).strftime(fmt)


def retry_with_backoff(func, max_retries=3, base_delay=0.1):
    """Retry a function with exponential backoff."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
    raise last_error
