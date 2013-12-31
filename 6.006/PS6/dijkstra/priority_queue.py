#!usr/bin/env python

class PriorityQueue:
    """Min-heap-based priority queue, using 1-based indexing. Adapted from CLRS.
    
    Augmented to include a map of keys to their indices in the heap so that
    key lookup is constant time and decrease_key(key) is O(log n) time.
    """
    
    def __init__(self):
        """Initializes the priority queue."""
        self.heap = [None] # To make the index 1-based.
        self.key_index = {} # key to index mapping.
    
    def __len__(self):
        return len(self.heap) - 1
       
    def __getitem__(self, i):
        return self.heap[i]

    def __setitem__(self, i, key):
        self.heap[i] = key

    def decrease_key(self, key):
        """Decreases the value of the key if it is in the priority queue and 
        maintains the heap property."""
        index = self.key_index[key]
        if index:
            self._decrease_key(index, key)
    
    def insert(self, key):
        """Inserts a key into the priority queue."""
        self.heap.append(key)
        self.key_index[key] = len(self)
        self._decrease_key(len(self), key)

    def extract_min(self):
        """Removes and returns the minimum key."""
        if len(self) < 1:
            return None
        self._swap(1, len(self))
        min = self.heap.pop()
        del self.key_index[min]
        self._min_heapify(1)
        return min
    
    def _decrease_key(self, i, key):
        """Decreases key at a give index.
        
        Args:
            i: index of the key.
            key: key with decreased value.
        """
        while i > 1:
            parent = i // 2
            if self[parent] > key:
                self._swap(i, parent)
                i = parent
            else:
                break
            
    def _min_heapify(self, i):
        """Restores the heap property from index i downwards."""
        l = 2 * i
        r = 2 * i + 1
        smallest = i
        if l <= len(self) and self[l] < self[i]:
            smallest = l
        if r <= len(self) and self[r] < self[smallest]:
            smallest = r
        if smallest != i:
            self._swap(i, smallest)
            self._min_heapify(smallest)

    def _swap(self, i, j):
        # Swaps the key at indices i and j and updates the key to index map.
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.key_index[self.heap[i]], self.key_index[self.heap[j]] = i, j

    def check_ri(self):
        heap = self.heap
        i = 1
        while i <= (len(heap) - 1) // 2:
            l = i * 2
            if heap[i] > heap[l]:
                raise ValueError('Left child is smaller than parent.')
            r = i * 2 + 1
            if r < len(heap) and heap[i] > heap[r]:
                raise ValueError('Right child is smaller than parent.')
            i += 1
            
        for key, index in self.key_index.items():
            if self.heap[index] is not key:
                raise ValueError('Key index mapping is wrong.')