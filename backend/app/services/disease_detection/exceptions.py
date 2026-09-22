class EngineException(Exception):
    """Base exception for Disease Detection Engine."""
    pass

class ImageProcessingError(EngineException):
    """Raised when an image cannot be parsed, is corrupt, or fails preprocessing."""
    pass

class ModelLoadError(EngineException):
    """Raised when the model weights or class mapping cannot be loaded correctly."""
    pass

class EngineInferenceError(EngineException):
    """Raised when the model forward pass fails."""
    pass
