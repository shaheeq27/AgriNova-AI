from PIL import Image, UnidentifiedImageError
from torchvision import transforms
import io
from .exceptions import ImageProcessingError

class ImagePreprocessor:
    def __init__(self):
        # Exact Phase 6.6 inference preprocessing (No augmentation)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def process(self, image_data: bytes) -> 'torch.Tensor':
        try:
            image = Image.open(io.BytesIO(image_data))
            # Safely convert to RGB (handles RGBA, grayscale, etc.)
            image = image.convert('RGB')
            tensor = self.transform(image)
            # Add batch dimension: [1, 3, 224, 224]
            return tensor.unsqueeze(0)
        except UnidentifiedImageError as e:
            raise ImageProcessingError("Uploaded data is not a valid or readable image.") from e
        except Exception as e:
            raise ImageProcessingError(f"Failed to preprocess image: {str(e)}") from e
