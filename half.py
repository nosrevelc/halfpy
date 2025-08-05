#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar efeito de Halftone (retícula) em uma imagem,
rotacionando somente a grade de pontos, não a própria imagem.

1. Instale dependências:
   py -m pip install Pillow numpy

2. Execute:
   py half.py "caminho/para/imagem.jpg" --block-size 8 --angle 45 --shape diamond --dpi 300

Argumentos:
  <input>            : caminho para a imagem de entrada.
  -o, --output       : caminho do PNG de saída (opcional).
  -b, --block-size   : tamanho do bloco da retícula (padrão: 10).
  --angle            : ângulo de rotação da grade em graus (padrão: 0).
  --shape            : circle | square | diamond (padrão: circle).
  --dpi              : DPI do PNG de saída (padrão: 300).
"""

import os
import sys
import math
import argparse
from PIL import Image, ImageDraw
import numpy as np

def halftone(img_path: str,
             block_size: int,
             output_path: str = None,
             angle: float = 0.0,
             shape: str = 'circle',
             dpi: int = 300) -> str:
    # abre a imagem e converte para RGBA (+ canal alfa)
    src = Image.open(img_path).convert('RGBA')
    gray = src.convert('L')

    w, h = src.size
    cx, cy = w/2, h/2
    angle_rad = math.radians(angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # nome automático se não passar output
    if not output_path:
        base, _ = os.path.splitext(img_path)
        output_path = f"{base}_halftone_b{block_size}_a{angle}_{shape}.png"

    # tela transparente
    out = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(out)

    # percorre grid original não rotacionado
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            # ponto de amostragem no centro do bloco
            samp_x = int(x + block_size/2)
            samp_y = int(y + block_size/2)

            # limita para não estourar bordas
            samp_x = min(max(samp_x, 0), w-1)
            samp_y = min(max(samp_y, 0), h-1)

            bright = gray.getpixel((samp_x, samp_y)) / 255.0
            color = src.getpixel((samp_x, samp_y))
            if color[3] == 0:
                continue

            # raio do ponto inverso ao brilho
            r = (block_size/2) * (1 - bright)
            if r < 0.5:
                continue

            # rotaciona somente a posição do ponto
            dx = x + block_size/2 - cx
            dy = y + block_size/2 - cy
            rot_x = dx * cos_a - dy * sin_a + cx
            rot_y = dx * sin_a + dy * cos_a + cy

            # desenha conforme o formato
            if shape == 'circle':
                bbox = (rot_x - r, rot_y - r, rot_x + r, rot_y + r)
                draw.ellipse(bbox, fill=color)
            elif shape == 'square':
                bbox = (rot_x - r, rot_y - r, rot_x + r, rot_y + r)
                draw.rectangle(bbox, fill=color)
            elif shape == 'diamond':
                pts = [
                    (rot_x,       rot_y - r),
                    (rot_x + r,   rot_y    ),
                    (rot_x,       rot_y + r),
                    (rot_x - r,   rot_y    )
                ]
                draw.polygon(pts, fill=color)

    # salva com o DPI desejado
    out.save(output_path, format='PNG', dpi=(dpi, dpi))
    print(f"[✔] Halftone salvo em: {output_path}")
    return output_path

def parse_args():
    p = argparse.ArgumentParser(description="Halftone rotacionado da grade, sem girar a imagem.")
    p.add_argument("input", help="Caminho para a imagem de entrada.")
    p.add_argument("-o","--output", help="PNG de saída (opcional).")
    p.add_argument("-b","--block-size", type=int, default=10,
                   help="Tamanho do bloco da retícula (padrão: 10).")
    p.add_argument("--angle", type=float, default=0.0,
                   help="Ângulo da grade em graus (padrão: 0).")
    p.add_argument("--shape", choices=['circle','square','diamond'],
                   default='circle', help="Forma do ponto (padrão: circle).")
    p.add_argument("--dpi", type=int, default=300,
                   help="DPI do PNG de saída (padrão: 300).")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        halftone(
            img_path     = args.input,
            block_size   = args.block_size,
            output_path  = args.output,
            angle        = args.angle,
            shape        = args.shape,
            dpi          = args.dpi
        )
    except FileNotFoundError as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
