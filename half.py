#!/usr/bin/env python
# Script para criar um efeito de Halftone (retícula) em uma imagem.
#
# 1. Instale dependências:
#    py -m pip install Pillow numpy
#
# 2. Execute:
#    py half.py "caminho/para/imagem.jpg" --block-size 8
#
from PIL import Image, ImageDraw
import numpy as np
import argparse
import os
import sys

def halftone(img_path: str, block_size: int, output_path: str = None) -> str:
    """
    Cria um efeito de halftone e retorna o caminho do arquivo de saída.
    Se output_path for None, gera um nome de arquivo automaticamente.
    """
    try:
        img = Image.open(img_path).convert('L')  # converter para tons de cinza
        if output_path is None:
            base, _ = os.path.splitext(img_path)
            output_path = f"{base}_halftone_b{block_size}.png"
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo não encontrado em '{img_path}'") from e

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
    print(f"[✔] Halftone salvo em: {output_path}")
    return output_path

def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Cria um efeito de halftone em uma imagem.")
    parser.add_argument("input", help="Caminho para a imagem de entrada.")
    parser.add_argument("-o", "--output", help="Caminho para o arquivo de saída. Se omitido, será gerado ao lado do original.")
    parser.add_argument("-b", "--block-size", type=int, default=10, help="Tamanho do bloco para os pontos da retícula (padrão: 10).")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input)
        output_file = f"{base}_halftone_b{args.block_size}.png"

    try:
        halftone(args.input, args.block_size, output_file)
    except FileNotFoundError as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
