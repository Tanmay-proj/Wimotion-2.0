from collections import deque
from typing import List, Optional
from .types import CSIRecord


class MultiLinkWindow:
    def __init__(self, seconds: float = 2.0, step: float = 0.5):
        self.seconds = seconds
        self.step = step
        self.records = deque()
        self.last_emit = None

    def add(self, record: CSIRecord) -> Optional[List[CSIRecord]]:
        self.records.append(record)
        cutoff = record.timestamp - self.seconds

        while self.records and self.records[0].timestamp < cutoff:
            self.records.popleft()

        if self.last_emit is None:
            self.last_emit = record.timestamp
            return list(self.records)

        if record.timestamp - self.last_emit >= self.step:
            self.last_emit = record.timestamp
            return list(self.records)

        return None

    def get_current(self) -> List[CSIRecord]:
        return list(self.records)

    def clear(self):
        self.records.clear()
        self.last_emit = None
