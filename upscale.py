#!/usr/bin/env python
# Como utilizar o script para redimensionar imagens
# Este script usa algoritmos de interpolação (como Lanczos) para alterar o tamanho.
# Não é um "upscaler" de IA, mas é rápido e não requer bibliotecas complexas.
#
# 1. Instale a dependência necessária (se ainda não tiver):
#    py -m pip install Pillow
#
# 2. Execute o script usando uma das opções abaixo:
#
#    - Para redimensionar por um fator (ex: dobrar o tamanho):
#      py upscale.py "caminho/para/imagem.jpg" -s 2.0
#
#    - Para redimensionar para dimensões exatas (ex: 800x600 pixels):
#      py upscale.py "caminho/para/imagem.png" -d 800 600
#
import sys
import os
import argparse
from PIL import Image

def upscale_image(input_path: str, scale_factor=None, target_width=None, target_height=None, resample_filter=Image.Resampling.LANCZOS) -> str:
    """
    Aumenta o tamanho de uma imagem usando o filtro escolhido.
    Salva o resultado como PNG e retorna o caminho de saída.
    """
    try:
        img = Image.open(input_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"O arquivo de entrada não foi encontrado em '{input_path}'") from e

    width, height = img.size
    print(f"[i] Carregando imagem: {input_path} ({width}x{height})")

    if scale_factor:
        new_width  = int(width  * scale_factor)
        new_height = int(height * scale_factor)
    else:
        new_width, new_height = target_width, target_height

    print(f"[i] Redimensionando para {new_width}x{new_height} usando o filtro {resample_filter.name}...")
    upscaled = img.resize((new_width, new_height), resample_filter)

    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_{new_width}x{new_height}.png"
    upscaled.save(output_path, format="PNG")
    print(f"[✔] Imagem redimensionada salva em: {output_path}")
    return output_path

def parse_args():
    parser = argparse.ArgumentParser(description="Upscale de imagem")
    parser.add_argument("input", help="Caminho para a imagem de entrada (JPG, PNG, etc.)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--scale", type=float,
                       help="Fator de escala (ex.: 2.0 para 200%% do tamanho)")
    group.add_argument("-d", "--dimensions", nargs=2, type=int, metavar=("WIDTH","HEIGHT"),
                       help="Dimensões exatas em pixels: -d largura altura")
    parser.add_argument("-r", "--resample", choices=["NEAREST","BILINEAR","BICUBIC","LANCZOS"],
                        default="LANCZOS", help="Filtro de interpolação (padrão: LANCZOS)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    filter_map = {
        "NEAREST": Image.Resampling.NEAREST,
        "BILINEAR": Image.Resampling.BILINEAR,
        "BICUBIC": Image.Resampling.BICUBIC,
        "LANCZOS": Image.Resampling.LANCZOS
    }
    resample = filter_map[args.resample]

    try:
        if args.scale:
            upscale_image(args.input, scale_factor=args.scale, resample_filter=resample)
        else:
            w, h = args.dimensions
            upscale_image(args.input, target_width=w, target_height=h, resample_filter=resample)
    except FileNotFoundError as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
