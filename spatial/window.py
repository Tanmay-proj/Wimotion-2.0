import threading
from collections import deque
from typing import List, Optional
from .types import CSIRecord


class MultiLinkWindow:
    def __init__(self, seconds: float = 2.0, step: float = 0.5):
        self.seconds = seconds
        self.step = step
        self.records = deque()
        self.last_emit = None
        self.lock = threading.Lock()

    def _get_time(self, record: CSIRecord) -> float:
        m = getattr(record, "monotonic_time", 0.0)
        return m if m > 0.0 else record.timestamp

    def add(self, record: CSIRecord) -> Optional[List[CSIRecord]]:
        with self.lock:
            self.records.append(record)
            t = self._get_time(record)
            cutoff = t - self.seconds

            while self.records and self._get_time(self.records[0]) < cutoff:
                self.records.popleft()

            if self.last_emit is None:
                self.last_emit = t
                return list(self.records)

            if t - self.last_emit >= self.step:
                self.last_emit = t
                return list(self.records)

            return None

    def get_current(self) -> List[CSIRecord]:
        with self.lock:
            return list(self.records)

    def clear(self):
        with self.lock:
            self.records.clear()
            self.last_emit = None
