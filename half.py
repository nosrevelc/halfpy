#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Halftone colorido com grade inclinada e reforço por N camadas semitransparentes,
sempre gerando PNG transparente pronto para DTF em fundo claro ou t-shirt preta.

1. Instale dependências:
   py -m pip install Pillow numpy

2. Execute:
   py halftone_rotate.py imagem.jpg \
       --block-size 10 --angle 45 --shape circle --dpi 300 \
       --background claro|escuro --layers 3
"""

import os
import sys
import math
import argparse
from PIL import Image, ImageDraw, ImageOps

def halftone_rotate(
    input_path: str,
    block_size: int,
    angle: float,
    shape: str,
    dpi: int,
    background: str,
    layers: int,
    output_path: str = None
) -> str:
    # 1) Carrega imagem
    orig_full = Image.open(input_path).convert("RGBA")
    w, h = orig_full.size
    gray_full = orig_full.convert("L")

    # 2) Detecta o fundo pelos cantos
    corners = [gray_full.getpixel((x,y)) for x,y in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    avg_corner = sum(corners)/4.0
    tol = 30
    need_bg = (
        (background=="claro" and avg_corner < 255-tol) or
        (background=="escuro" and avg_corner > tol)
    )

    # 3) Se modo claro e sem fundo adequado, compõe branco antes de amostrar
    if background=="claro" and need_bg:
        bg_img = Image.new("RGBA",(w,h),(255,255,255,255))
        orig = Image.alpha_composite(bg_img, orig_full)
        print("[i] Inserido fundo branco para amostragem.")
    else:
        orig = orig_full

    gray_base = orig.convert("L")

    # 3b) Ajusta imagem conforme o fundo de destino:
    #     - fundo claro => inverte como no fluxo do Photoshop para camisetas brancas
    #     - fundo escuro => mantém as cores originais
    if background == "claro":
        inverted_rgb = ImageOps.invert(orig.convert("RGB"))
        r, g, b = inverted_rgb.split()
        color_img = Image.merge("RGBA", (r, g, b, orig.split()[-1]))
        def intensity(ix, iy):
            return 1.0 - (gray_base.getpixel((ix, iy)) / 255.0)
    else:
        color_img = orig
        def intensity(ix, iy):
            return gray_base.getpixel((ix, iy)) / 255.0

    # 4) Gera nome de saída
    if not output_path:
        base,_ = os.path.splitext(input_path)
        output_path = f"{base}_halftone_b{block_size}_a{angle}_{shape}_{background}_x{layers}.png"

    # 5) Cria camada base transparente
    base_layer = Image.new("RGBA",(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(base_layer)

    # 6) Pré-calcula trigonometria e parâmetros
    theta = math.radians(angle)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    max_radius = max(1.0, float(block_size))
    diag = math.hypot(w,h)
    start, end = -diag/2, diag/2

    # 7) Calcula alpha semitransparente para empilhar
    fill_alpha = max(1, min(255, int(255/layers)))

    # 8) Define função de cálculo de raio e cor (incluindo alpha)
    def compute(bright, px_color):
        return (max_radius*bright, (px_color[0], px_color[1], px_color[2], fill_alpha))

    # 9) Varre a grade inclinada e desenha no base_layer
    u = start
    while u <= end:
        v = start
        while v <= end:
            x = u*cos_t - v*sin_t + w/2
            y = u*sin_t + v*cos_t + h/2
            if 0<=x<w and 0<=y<h:
                ix,iy = int(x),int(y)
                bright = intensity(ix, iy)
                px_color = color_img.getpixel((ix,iy))
                if px_color[3]!=0:
                    r, fill = compute(bright, px_color)
                    if r>=0.5:
                        if shape=="circle":
                            draw.ellipse((x-r,y-r,x+r,y+r), fill=fill)
                        elif shape=="square":
                            draw.rectangle((x-r,y-r,x+r,y+r), fill=fill)
                        else:
                            pts = [(x,y-r),(x+r,y),(x,y+r),(x-r,y)]
                            draw.polygon(pts, fill=fill)
            v += block_size
        u += block_size

    # 10) Empilha a camada semitransparente N vezes
    intensified = base_layer.copy()
    for i in range(layers-1):
        intensified = Image.alpha_composite(intensified, base_layer)

    # 11) Salva sempre um PNG transparente
    intensified.save(output_path, format="PNG", dpi=(dpi,dpi))
    print(f"[OK] Halftone salvo em: {output_path}")
    return output_path

def parse_args():
    p = argparse.ArgumentParser(
        description="Halftone colorido com boost via N camadas semitransparentes"
    )
    p.add_argument("input", help="Imagem de entrada (JPG, PNG etc.)")
    p.add_argument("-o","--output", help="PNG de saída (opcional)")
    p.add_argument("-b","--block-size", type=int, default=35,
                   help="Tamanho do bloco/ponto da grade (padrão:35)")
    p.add_argument("--angle", type=float, default=45.0,
                   help="Ângulo da grade em graus (padrão:45)")
    p.add_argument("--shape", choices=["circle","square","diamond"],
                   default="circle", help="Forma do ponto (padrão:circle)")
    p.add_argument("--dpi", type=int, default=300,
                   help="DPI do PNG de saída (padrão:300)")
    p.add_argument("--background", choices=["claro","escuro"],
                   help="‘claro’ ou ‘escuro’ (pergunta se omisso)")
    p.add_argument("--layers", type=int, default=3,
                   help="Número de camadas semitransparentes (padrão:3)")
    return p.parse_args()

if __name__=="__main__":
    args = parse_args()
    if args.layers<1:
        print("[✖] ERRO: --layers deve ser >=1", file=sys.stderr)
        sys.exit(1)
    bg = args.background
    if not bg:
        escolha = input("Fundo claro ou escuro? [claro/escuro]: ").strip().lower()
        bg = "escuro" if escolha in ("escuro","dark","preto") else "claro"
    try:
        halftone_rotate(
            input_path  = args.input,
            block_size  = args.block_size,
            angle       = args.angle,
            shape       = args.shape,
            dpi         = args.dpi,
            background  = bg,
            layers      = args.layers,
            output_path = args.output
        )
    except Exception as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
