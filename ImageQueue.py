from __future__ import annotations
from queue import Queue
from typing import List

class ImageQueue(Queue):

    def __init__(self, items: List = None):

        super().__init__()

        if items is not None:
            self.initialize(items)
        else:
            self.qsize_initial = 0

    def initialize(self, items: List) -> ImageQueue:
        for item in items:
            self.put(item)
        self.qsize_initial = self.qsize()
        return self
    
    def __repr__(self) -> str:
        return f"({self.qsize_initial - self.qsize()}/{self.qsize_initial})"

