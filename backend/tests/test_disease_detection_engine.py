import pytest
import io
import json
import torch
from PIL import Image
import numpy as np

from app.services.disease_detection.engine import DiseaseDetectionEngine
from app.services.disease_detection.preprocessor import ImagePreprocessor
from app.services.disease_detection.exceptions import ImageProcessingError, ModelLoadError
from app.services.disease_detection.schemas import DiseaseDetectionResult

# Mock valid image bytes
def create_test_image(color=(255, 0, 0), size=(300, 300), mode='RGB'):
    img = Image.new(mode, size, color=color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG' if mode != 'RGBA' else 'PNG')
    return buf.getvalue()

def test_preprocessing_shape_and_rgb_conversion():
    # Covers: 1. preprocessing shape, 2. RGB conversion
    preprocessor = ImagePreprocessor()

    # Test RGB image
    rgb_bytes = create_test_image(mode='RGB')
    tensor_rgb = preprocessor.process(rgb_bytes)
    assert tensor_rgb.shape == (1, 3, 224, 224), f"Expected shape [1,3,224,224], got {tensor_rgb.shape}"

    # Test RGBA image (should convert to RGB)
    rgba_bytes = create_test_image(color=(255, 0, 0, 128), mode='RGBA')
    tensor_rgba = preprocessor.process(rgba_bytes)
    assert tensor_rgba.shape == (1, 3, 224, 224), f"Expected shape [1,3,224,224], got {tensor_rgba.shape}"

def test_invalid_image_handling():
    # Covers: 3. invalid/corrupt image handling
    preprocessor = ImagePreprocessor()
    with pytest.raises(ImageProcessingError):
        preprocessor.process(b"not an image bytes")

def test_model_loading_and_class_mapping():
    # Covers: 4. class mapping, 8. model loading, 10. missing/corrupt model artifact handling

    # Valid loading
    engine = DiseaseDetectionEngine()
    assert engine.model is not None
    assert engine._initialized is True
    assert len(engine.idx_to_class) == 12

    # Missing files
    DiseaseDetectionEngine._instance = None # Reset singleton
    with pytest.raises(ModelLoadError):
        DiseaseDetectionEngine(model_path="/fake/path.pth")

    DiseaseDetectionEngine._instance = None
    with pytest.raises(ModelLoadError):
        DiseaseDetectionEngine(mapping_path="/fake/mapping.json")

    # Recover singleton for next tests
    DiseaseDetectionEngine._instance = None

def test_inference_and_outputs():
    # Covers: 5. healthy-class detection, 6. probability range, 7. probability ordering, 9. deterministic inference
    engine = DiseaseDetectionEngine()

    img_bytes = create_test_image(color=(0, 255, 0)) # Green test image

    result = engine.predict(img_bytes)
    assert isinstance(result, DiseaseDetectionResult)
    assert len(result.predictions) == 12

    prob_sum = 0.0
    prev_prob = 1.1
    for pred in result.predictions:
        # 6. probability range
        assert 0.0 <= pred.probability <= 1.0
        # 7. probability ordering (descending)
        assert pred.probability <= prev_prob
        prev_prob = pred.probability
        prob_sum += pred.probability

        # 5. healthy-class detection
        if "Healthy" in pred.disease:
            assert pred.is_healthy is True
        else:
            assert pred.is_healthy is False

    # Softmax probabilities should sum to ~1.0
    assert abs(prob_sum - 1.0) < 1e-5

    # 9. deterministic inference (predicting twice yields exactly the same probabilities)
    result2 = engine.predict(img_bytes)
    for p1, p2 in zip(result.predictions, result2.predictions):
        assert p1.crop == p2.crop
        assert p1.disease == p2.disease
        assert abs(p1.probability - p2.probability) < 1e-6
