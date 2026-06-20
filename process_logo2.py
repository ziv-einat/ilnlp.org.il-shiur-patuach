from rembg import remove
from PIL import Image

src = r"C:\Users\zivei\WhatsApp Image 2026-06-15 at 22.43.20.jpeg"
dst = r"C:\Users\zivei\logo_nlp.png"

img = Image.open(src).convert("RGBA")
result = remove(img)
result.save(dst)
print("Done:", dst)
