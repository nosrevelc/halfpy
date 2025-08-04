# Como utilizar o script para remover fundo de imagens
# 1. Instale as dependências necessárias:  py -m pip install onnxruntime rembg Pillow
# 2. Execute o script passando o caminho da imagem como argumento: py remove_bg.py
#!/usr/bin/env python
import sys
import os
import io
from rembg import remove
from PIL import Image

def process_image_to_png(input_path, dpi=300):
    """
    Remove background via rembg, converte para RGBA, define DPI e salva como PNG.
    """
    # 1. Lê bytes da imagem de entrada (JPG, PNG, TIFF etc.)
    with open(input_path, 'rb') as f:
        input_data = f.read()

    # 2. Remove o fundo usando rembg
    output_data = remove(input_data)

    # 3. Abre o resultado e garante canal alpha
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # 4. Prepara caminho de saída
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_{dpi}dpi.png"

    # 5. Salva em PNG com transparência e DPI definido
    img.save(output_path, format="PNG", dpi=(dpi, dpi))

    print(f"[✔] Processado e salvo: {output_path}")

if __name__ == "__main__":
    if not (2 <= len(sys.argv) <= 3):
        print("Uso: py process_to_png.py <caminho_da_imagem> [dpi]")
        sys.exit(1)

    arquivo = sys.argv[1]
    valor_dpi = int(sys.argv[2]) if len(sys.argv) == 3 else 300
    process_image_to_png(arquivo, valor_dpi)

   