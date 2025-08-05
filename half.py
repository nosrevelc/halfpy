#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Halftone colorido com grade inclinada sem girar a imagem original.

1. Instale dependências:
   py -m pip install Pillow numpy

2. Execute:
   py halftone_rotate.py "caminho/para/imagem.jpg" \
       --block-size 10 --angle 45 --shape circle --dpi 300

Parâmetros:
  input         : Caminho da imagem (JPG, PNG etc.)
  -o, --output  : Arquivo de saída (opcional). Padrão: <input>_halftone.png
  -b, --block-size : Tamanho do bloco/ponto da grade (padrão: 10)
  --angle       : Ângulo da grade em graus (padrão: 0)
  --shape       : circle | square | diamond (padrão: circle)
  --dpi         : DPI do PNG de saída (padrão: 300)
"""

import os
import sys
import math
import argparse
from PIL import Image, ImageDraw


def halftone_rotate(
    input_path: str,
    block_size: int,
    angle: float,
    shape: str,
    dpi: int,
    output_path: str = None
) -> str:
    # --- Carrega imagens ---
    orig = Image.open(input_path).convert("RGBA")
    gray = orig.convert("L")
    w, h = orig.size
    cx, cy = w/2, h/2

    # --- Nome de saída automático ---
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_halftoneRotate_b{block_size}_a{angle}_{shape}.png"

    # --- Canvas de saída (transparente) ---
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)

    # --- Pré-calcula trigonometria ---
    theta = math.radians(angle)
    cos_t, sin_t = math.cos(theta), math.sin(theta)

    # --- Raio da circunferência de amostragem na grid original ---
    half = block_size / 2

    # --- Tamanho mínimo da grade para cobrir a imagem ao girar ---
    # A diagonal da imagem
    diag = math.hypot(w, h)
    # Vamos varrer u,v de -diag/2 até +diag/2
    start = -diag/2
    end = diag/2

    u = start
    while u <= end:
        v = start
        while v <= end:
            # Posição rotacionada no canvas de saída
            x = u * cos_t - v * sin_t + cx
            y = u * sin_t + v * cos_t + cy

            # Somente pontos dentro da imagem
            if 0 <= x < w and 0 <= y < h:
                ix, iy = int(x), int(y)
                # Amostra brilho e cor originais
                b = gray.getpixel((ix, iy)) / 255.0
                color = orig.getpixel((ix, iy))
                if color[3] == 0:
                    v += block_size
                    continue

                # Raio proporcional (pontos maiores em áreas escuras)
                r = half * (1 - b)
                if r >= 0.5:
                    # Desenha a forma
                    if shape == "circle":
                        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
                    elif shape == "square":
                        draw.rectangle((x - r, y - r, x + r, y + r), fill=color)
                    elif shape == "diamond":
                        pts = [
                            (x,     y - r),
                            (x + r, y    ),
                            (x,     y + r),
                            (x - r, y    )
                        ]
                        draw.polygon(pts, fill=color)

            v += block_size
        u += block_size

    # --- Salva resultado com DPI ---
    out.save(output_path, format="PNG", dpi=(dpi, dpi))
    print(f"[✔] Halftone salvo em: {output_path}")
    return output_path


def parse_args():
    p = argparse.ArgumentParser(
        description="Halftone colorido com grade inclinada"
    )
    p.add_argument("input", help="Imagem de entrada (JPG, PNG etc.)")
    p.add_argument(
        "-o", "--output",
        help="PNG de saída (opcional)"
    )
    p.add_argument(
        "-b", "--block-size",
        type=int, default=10,
        help="Tamanho do bloco/ponto da grade"
    )
    p.add_argument(
        "--angle",
        type=float, default=0.0,
        help="Ângulo da grade em graus"
    )
    p.add_argument(
        "--shape",
        choices=["circle", "square", "diamond"],
        default="circle",
        help="Forma do ponto"
    )
    p.add_argument(
        "--dpi",
        type=int, default=300,
        help="DPI para o PNG de saída"
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        halftone_rotate(
            input_path=args.input,
            block_size=args.block_size,
            angle=args.angle,
            shape=args.shape,
            dpi=args.dpi,
            output_path=args.output
        )
    except FileNotFoundError as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
