#!/usr/bin/env python
# Script para aplicar um filtro de nitidez (sharpen) a uma imagem.
#
# 1. Instale a dependência necessária (se ainda não tiver):
#    py -m pip install Pillow
#
# 2. Execute o script:
#    py sharpen.py "caminho/para/imagem.jpg"
#
import sys
import os
import argparse
from PIL import Image, ImageFilter

def sharpen_image(input_path: str, output_path: str = None, dpi: int = 300) -> str:
    """
    Aplica um filtro de nitidez (sharpen) e salva a imagem como PNG.
    Retorna o caminho do arquivo de saída.
    """
    try:
        img = Image.open(input_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de entrada não encontrado em '{input_path}'")

    # Converte para 'RGB' para garantir compatibilidade e remover canal alfa
    img_rgb = img.convert('RGB')
    sharpened_img = img_rgb.filter(ImageFilter.SHARPEN)

    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_sharpened.png"

    sharpened_img.save(output_path, format="PNG", dpi=(dpi, dpi))
    print(f"[✔] Imagem com nitidez aplicada salva em: {output_path}")
    return output_path

def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Aplica um filtro de nitidez (sharpen) em uma imagem.")
    parser.add_argument("input", help="Caminho para a imagem de entrada.")
    parser.add_argument("-o", "--output", help="Caminho para o arquivo de saída (opcional).")
    parser.add_argument("--dpi", type=int, default=300, help="DPI para o arquivo de saída (padrão: 300).")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        sharpen_image(args.input, args.output, args.dpi)
    except (FileNotFoundError, IOError) as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)