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
import math
import os
import sys

def halftone(img_path: str, block_size: int, output_path: str = None, angle: float = 0, shape: str = 'circle', dpi: int = 300) -> str:
    """
    Cria um efeito de halftone colorido, sem redimensionar, em CMYK e com DPI customizável.
    Se output_path for None, gera um nome de arquivo automaticamente.
    """
    try:
        # Abre a imagem original e converte para RGBA para cor e transparência
        source_img = Image.open(img_path).convert('RGBA')
        # Cria uma versão em tons de cinza para análise de brilho
        grayscale_img = source_img.convert('L')

        if output_path is None:
            base, _ = os.path.splitext(img_path)
            # Adiciona os novos parâmetros ao nome do arquivo para clareza
            output_path = f"{base}_halftone_CMYK_b{block_size}_a{angle}_{shape}.tif"
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo não encontrado em '{img_path}'") from e

    width, height = source_img.size

    # 1. Cria uma nova imagem RGBA transparente para desenhar os pontos coloridos
    halftone_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(halftone_img)

    # 2. Prepara para a rotação matemática
    angle_rad = math.radians(angle)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    center_x, center_y = width / 2, height / 2

    # 3. Itera sobre a tela de destino e calcula a cor de origem
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Centro do bloco atual na imagem de destino
            dest_cx, dest_cy = x + block_size / 2, y + block_size / 2

            # Aplica a rotação inversa para encontrar o ponto correspondente na imagem de origem
            # Translação para a origem, rotação e translação de volta
            src_x = int((dest_cx - center_x) * cos_angle - (dest_cy - center_y) * sin_angle + center_x)
            src_y = int((dest_cx - center_x) * sin_angle + (dest_cy - center_y) * cos_angle + center_y)

            # Se o ponto de origem estiver fora dos limites, pula
            if not (0 <= src_x < width and 0 <= src_y < height):
                continue

            # Obtém o brilho e a cor do ponto de origem
            brightness = grayscale_img.getpixel((src_x, src_y))
            color = source_img.getpixel((src_x, src_y))

            # Se a cor de origem for totalmente transparente, não desenha nada
            if color[3] == 0:
                continue

            # O raio é inversamente proporcional ao brilho (preto = ponto grande, branco = ponto pequeno)
            radius = (block_size / 2) * (1 - brightness / 255)

            if radius < 0.5:  # Não desenha pontos insignificantes
                continue

            # Usa a cor do ponto de origem para preencher a forma
            if shape == 'circle':
                draw.ellipse((dest_cx - radius, dest_cy - radius, dest_cx + radius, dest_cy + radius), fill=color)
            elif shape == 'square':
                draw.rectangle((dest_cx - radius, dest_cy - radius, dest_cx + radius, dest_cy + radius), fill=color)
            elif shape == 'diamond':
                points = [
                    (dest_cx, dest_cy - radius), (dest_cx + radius, dest_cy),
                    (dest_cx, dest_cy + radius), (dest_cx - radius, dest_cy)
                ]
                draw.polygon(points, fill=color)

    # 4. Converte a imagem de halftone (RGBA) para CMYK
    # Cria um fundo branco em CMYK. (0,0,0,0) em CMYK é branco.
    cmyk_background = Image.new('CMYK', (width, height), (0, 0, 0, 0))

    # Converte a imagem de halftone para RGB (necessário para colar em CMYK)
    # A transparência (canal alfa) será usada como máscara
    rgb_halftone = halftone_img.convert('RGB')
    alpha_mask = halftone_img.split()[3]

    # Cola a imagem RGB sobre o fundo CMYK, usando a transparência como máscara
    cmyk_background.paste(rgb_halftone, (0, 0), mask=alpha_mask)

    # 5. Salva a imagem final em formato TIFF com o DPI especificado
    cmyk_background.save(
        output_path,
        format='TIFF',
        dpi=(dpi, dpi),
        compression='tiff_lzw' # Compressão sem perdas
    )
    print(f"[✔] Halftone CMYK ({dpi} DPI) salvo em: {output_path}")
    return output_path

def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Cria um efeito de halftone em uma imagem.")
    parser.add_argument("input", help="Caminho para a imagem de entrada.")
    parser.add_argument("-o", "--output", help="Caminho para o arquivo de saída (opcional).")
    parser.add_argument("-b", "--block-size", type=int, default=10, help="Tamanho do bloco (frequência) da retícula (padrão: 10).")
    parser.add_argument("--angle", type=float, default=0.0, help="Ângulo da retícula em graus (ex: 45). Padrão: 0.")
    parser.add_argument("--shape", choices=['circle', 'square', 'diamond'], default='circle', help="Forma do ponto da retícula. Padrão: circle.")
    parser.add_argument("--dpi", type=int, default=300, help="DPI para o arquivo de saída (padrão: 300).")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        # A função halftone agora lida com a nomeação do arquivo de saída e os novos parâmetros
        halftone(args.input, args.block_size, args.output, args.angle, args.shape, args.dpi)
    except FileNotFoundError as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
