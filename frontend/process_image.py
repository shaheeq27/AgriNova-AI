from PIL import Image
import numpy as np

img = Image.open('/Users/shaheeq.s/.gemini/antigravity/brain/e41ed62e-1e22-43c0-bd53-e33f063c18f7/.user_uploaded/media_1788939293798.jpg').convert('RGB')
arr = np.array(img).astype(np.float32)

# Calculate alpha as the maximum of RGB channels
alpha = np.max(arr, axis=2)

# Avoid division by zero
alpha_safe = np.where(alpha == 0, 1, alpha)

# Un-premultiply
r = np.clip(arr[:,:,0] * 255.0 / alpha_safe, 0, 255)
g = np.clip(arr[:,:,1] * 255.0 / alpha_safe, 0, 255)
b = np.clip(arr[:,:,2] * 255.0 / alpha_safe, 0, 255)

out = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
out[:,:,0] = r
out[:,:,1] = g
out[:,:,2] = b
out[:,:,3] = alpha

Image.fromarray(out).save('public/hero-crop.png')
print("Saved to public/hero-crop.png")
