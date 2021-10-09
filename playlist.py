from collections import deque

class Playlist:
    """Stores the youtube links of songs to be played and already played and offers basic operation on the queues"""

    def __init__(self):
        # Stores the ytlinks os the songs in queue and the ones already played
        self.playque = deque()

    def __len__(self):
        return len(self.playque)

    def __getitem__(self, index):
        return self.playque[index]

    def add(self, songrequest):
        self.playque.append(songrequest)

    def empty(self):
        self.playque.clear()

    def popleft(self):
        return self.playque.popleft()
