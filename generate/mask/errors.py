"""Error classes for mask generation."""


class InvalidMaskError(Exception):
    """Raised when a generated mask violates validation constraints."""
    pass


class MaskDensityExceeded(Exception):
    """Raised when mask density exceeds configured threshold."""
    pass
