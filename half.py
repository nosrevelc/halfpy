from PIL import Image, ImageDraw
import numpy as np

def halftone(img_path, block_size=10, output_path='halftone.png'):
    img = Image.open(img_path).convert('L')  # converter para tons de cinza
    width, height = img.size
    pixels = np.array(img)

    new_img = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(new_img)

    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            block = pixels[y:y+block_size, x:x+block_size]
            avg = np.mean(block)
            radius = block_size * (1 - avg / 255) / 2
            cx, cy = x + block_size // 2, y + block_size // 2
            draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=0
            )

    new_img.save(output_path)
    print(f"Halftone salvo em {output_path}")
