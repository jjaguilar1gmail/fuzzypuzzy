"""Utilities: RNG

Contains the RNG class for random number utilities.
"""
import random
import time

class RNG:
    """Seeded random number generator for reproducible puzzle generation."""
    
    def __init__(self, seed=None):
        """Initialize with seed. If None, uses current time."""
        if seed is None:
            seed = int(time.time() * 1000) % (2**31)
        self.seed = seed
        self.rng = random.Random(seed)
    
    def randint(self, a, b):
        """Random integer in range [a, b]."""
        return self.rng.randint(a, b)
    
    def choice(self, seq):
        """Random choice from sequence."""
        return self.rng.choice(seq)
    
    def shuffle(self, seq):
        """Shuffle sequence in place."""
        return self.rng.shuffle(seq)
    
    def random(self):
        """Random float in [0.0, 1.0)."""
        return self.rng.random()
    
    def get_seed(self):
        """Return the current seed."""
        return self.seed
