from rembg import remove
from PIL import Image
import numpy as np
from scipy import ndimage

src = r"C:\Users\zivei\OneDrive\תמונות\Screenshots\צילום מסך 2026-06-15 222946.png"
dst = r"C:\Users\zivei\logo_nlp.png"

# Step 1: remove background with AI
img = Image.open(src).convert("RGBA")
print(f"Image size: {img.size}")
result = remove(img)
data = np.array(result)

# Step 2: find red badge by color
r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
red_mask = (r.astype(int) - g.astype(int) > 35) & (r > 120) & (b < 140) & (a > 30)

# Step 3: label connected components — keep only badge-sized red blobs
labeled, num = ndimage.label(red_mask)
print(f"Red components found: {num}")
for i in range(1, num + 1):
    component = labeled == i
    size = component.sum()
    ys, xs = np.where(component)
    print(f"  Component {i}: size={size}, x={xs.min()}-{xs.max()}, y={ys.min()}-{ys.max()}")
    # Remove any red blob that is large enough to be the badge
    if size > 500:
        # Remove red pixels
        data[component] = [0, 0, 0, 0]
        # Also erase the entire bounding box (catches white text inside badge)
        y1, y2 = int(ys.min()), int(ys.max()) + 1
        x1, x2 = int(xs.min()), int(xs.max()) + 1
        data[y1:y2, x1:x2] = [0, 0, 0, 0]
        print(f"  -> Erased bounding box [{x1}:{x2}, {y1}:{y2}]")

out = Image.fromarray(data)
out.save(dst)
print("Done:", dst)
