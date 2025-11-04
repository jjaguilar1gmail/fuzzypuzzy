"""App façade: Presets

Contains the Presets class for preset sizes and difficulties.
"""

class Presets:
    """Predefined puzzle configurations."""
    
    SUPPORTED_SIZES = {
        "5x5": (5, 5),
        "7x7": (7, 7)
    }
    
    @staticmethod
    def get_size(size_str):
        """Get (rows, cols) for a size string like '5x5'."""
        if size_str not in Presets.SUPPORTED_SIZES:
            supported = ", ".join(Presets.SUPPORTED_SIZES.keys())
            raise ValueError(f"Unsupported size '{size_str}'. Supported: {supported}")
        return Presets.SUPPORTED_SIZES[size_str]
    
    @staticmethod
    def get_default_config(size_str, difficulty="easy"):
        """Get default generation config for a size and difficulty."""
        rows, cols = Presets.get_size(size_str)
        
        return {
            "rows": rows,
            "cols": cols,
            "difficulty": difficulty,
            "path_mode": "serpentine",
            "clue_mode": "even"
        }
