#!/usr/bin/env python
# Processador de Imagens - Canivete Suíço
#
# Este script unifica todas as ferramentas de processamento de imagem.
#
# 1. Instale todas as dependências de uma vez:
#    py -m pip install -r requirements.txt
#
# 2. Execute usando os sub-comandos. Exemplo:
#    py process.py remove-bg "imagem.jpg"
#
import argparse
import sys 
import os
from PIL import Image, ImageFilter

# --- Importar as funções principais dos outros scripts ---
try:
    from remove_bg import process_image_to_png
    from ai_enhance import ai_enhance, VALID_MODELS
    from upscale import upscale_image
    from half import halftone
    from sharpen import sharpen_image
except ImportError as e:
    print(f"[✖] Erro ao importar um módulo necessário: {e}", file=sys.stderr)
    print("    Certifique-se que todos os scripts (remove_bg.py, ai_enhance.py, etc.) estão na mesma pasta.", file=sys.stderr)
    sys.exit(1)

# --- Funções de execução para cada sub-comando ---

def run_remove_bg(args: argparse.Namespace):
    """Executa a remoção de fundo."""
    print("--- Executando Remoção de Fundo ---")
    process_image_to_png(args.input, args.dpi)

def run_ai_enhance(args: argparse.Namespace):
    """Executa a super-resolução com IA."""
    print("--- Executando Super-Resolução IA ---")
    ai_enhance(args.input, args.model, args.scale, args.models_path)

def run_upscale(args: argparse.Namespace):
    """Executa o redimensionamento padrão."""
    print("--- Executando Redimensionamento Padrão ---")
    filter_map = {
        "nearest": Image.Resampling.NEAREST,
        "bilinear": Image.Resampling.BILINEAR,
        "bicubic": Image.Resampling.BICUBIC,
        "lanczos": Image.Resampling.LANCZOS
    }
    # Garante que a escolha do filtro não seja sensível a maiúsculas/minúsculas
    resample_filter = filter_map[args.resample.lower()]

    if args.scale:
        upscale_image(args.input, scale_factor=args.scale, resample_filter=resample_filter)
    elif args.dimensions:
        w, h = args.dimensions
        upscale_image(args.input, target_width=w, target_height=h, resample_filter=resample_filter)

def run_halftone(args: argparse.Namespace):
    """
    Executa o efeito de retícula (halftone).
    A lógica para nomear o arquivo de saída agora está centralizada na função `halftone`.
    """
    print("--- Executando Efeito Halftone ---")
    # Passamos `args.output` diretamente. A função `halftone` saberá o que fazer se for None.
    halftone(args.input, args.block_size, args.output, args.angle, args.shape, args.dpi)

def run_sharpen(args: argparse.Namespace):
    """Aplica um filtro de nitidez (sharpen)."""
    print("--- Aplicando Filtro de Nitidez ---")
    sharpen_image(args.input, args.output, args.dpi)

# --- Configuração do Parser Principal ---

def main():
    parser = argparse.ArgumentParser(
        description="Processador de Imagens - Um canivete suíço para suas imagens.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Comando a ser executado')

    # --- Sub-comando: remove-bg ---
    p_rmbg = subparsers.add_parser('remove-bg', help='Remove o fundo de uma imagem (usa rembg).')
    p_rmbg.add_argument('input', help='Imagem de entrada.')
    p_rmbg.add_argument('--dpi', type=int, default=300, help='DPI para o PNG de saída (padrão: 300).')
    p_rmbg.set_defaults(func=run_remove_bg)

    # --- Sub-comando: enhance ---
    p_enhance = subparsers.add_parser('enhance', help='Aumenta a resolução com IA (ex: EDSR, LapSRN).')
    p_enhance.add_argument("input", help="Imagem de entrada (JPG, PNG etc.)")
    p_enhance.add_argument("-m","--model", type=str.upper, choices=list(VALID_MODELS.keys()), default="EDSR", help="Modelo de IA a ser usado (não diferencia maiúsculas/minúsculas).")
    p_enhance.add_argument("-s","--scale", type=int, default=4, help="Fator de escala (ex: 2, 3, 4).")
    p_enhance.add_argument("--models-path", help="Caminho para a pasta com modelos .pb locais, evitando o download.")
    p_enhance.set_defaults(func=run_ai_enhance)

    # --- Sub-comando: upscale ---
    p_upscale = subparsers.add_parser('upscale', help='Redimensiona imagem com filtros padrão (ex: Lanczos).')
    p_upscale.add_argument("input", help="Imagem de entrada.")
    group = p_upscale.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--scale", type=float, help="Fator de escala (ex: 2.0 para 200%%).")
    group.add_argument("-d", "--dimensions", nargs=2, type=int, metavar=("W", "H"), help="Dimensões exatas (largura altura).")
    p_upscale.add_argument("-r", "--resample", choices=["nearest", "bilinear", "bicubic", "lanczos"], default="lanczos", help="Filtro de interpolação (padrão: lanczos).", type=str.lower)
    p_upscale.set_defaults(func=run_upscale)

    # --- Sub-comando: halftone ---
    p_half = subparsers.add_parser('halftone', help='Aplica efeito de retícula (halftone) na imagem.')
    p_half.add_argument("input", help="Caminho para a imagem de entrada.")
    p_half.add_argument("-o", "--output", help="Caminho para o arquivo de saída (opcional).")
    p_half.add_argument("-b", "--block-size", type=int, default=10, help="Tamanho do bloco (frequência) da retícula (padrão: 10).")
    p_half.add_argument("--angle", type=float, default=0.0, help="Ângulo da retícula em graus (ex: 45). Padrão: 0.")
    p_half.add_argument("--shape", choices=['circle', 'square', 'diamond'], default='circle', help="Forma do ponto da retícula. Padrão: circle.")
    p_half.add_argument("--dpi", type=int, default=300, help="DPI para o arquivo de saída (padrão: 300).")
    p_half.set_defaults(func=run_halftone)

    # --- Sub-comando: sharpen ---
    p_sharpen = subparsers.add_parser('sharpen', help='Aplica um filtro de nitidez na imagem.')
    p_sharpen.add_argument("input", help="Caminho para a imagem de entrada.")
    p_sharpen.add_argument("-o", "--output", help="Caminho para o arquivo de saída (opcional).")
    p_sharpen.add_argument("--dpi", type=int, default=300, help="DPI para o arquivo de saída (padrão: 300).")
    p_sharpen.set_defaults(func=run_sharpen)

    try:
        args = parser.parse_args()

        # Validação extra para combinações de argumentos que o argparse não consegue fazer nativamente
        if args.command == 'enhance' and args.scale not in VALID_MODELS[args.model]:
            raise ValueError(
                f"Modelo '{args.model}' não suporta a escala x{args.scale}. "
                f"Opções válidas para este modelo: {VALID_MODELS[args.model]}"
            )

        args.func(args)
        print("\n[✔] Operação concluída com sucesso!")
    except (FileNotFoundError, ValueError, RuntimeError, IOError) as e:
        # Captura erros conhecidos e exibe uma mensagem amigável
        print(f"\n[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()