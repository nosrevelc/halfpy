# Como utilizar o script para remover fundo de imagens
#
# 1. Instale as dependências necessárias:
#    py -m pip install rembg Pillow onnxruntime
#    (Atenção: A primeira execução pode precisar de internet para baixar os modelos de IA)
#
# 2. Execute o script passando o caminho da imagem e o DPI (opcional):
#
#    - Para remover o fundo com o DPI padrão (300):
#      py remove_bg.py "caminho/para/sua/imagem.jpg"
#
#    - Para remover o fundo e definir um DPI específico (ex: 600):
#      py remove_bg.py "caminho/para/sua/imagem.png" 600
#
# O script salvará um novo arquivo PNG com o sufixo "_300dpi.png" (ou o DPI escolhido).
#!/usr/bin/env python
import sys
import os
import io
import argparse
from rembg import remove
from PIL import Image

def process_image_to_png(input_path: str, dpi: int = 300) -> str:
    """
    Remove background via rembg, converte para RGBA, define DPI e salva como PNG.
    Retorna o caminho do arquivo de saída.
    """
    try:
        # 1. Lê bytes da imagem de entrada (JPG, PNG, TIFF etc.)
        with open(input_path, 'rb') as f:
            input_data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de entrada não encontrado em '{input_path}'")
    except Exception as e:
        raise IOError(f"Falha ao ler o arquivo '{input_path}': {e}") from e

    # 2. Remove o fundo usando rembg
    output_data = remove(input_data)

    # 3. Abre o resultado e garante canal alpha
    img = Image.open(io.BytesIO(output_data)).convert("RGBA")

    # 4. Prepara caminho de saída
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_nobg_{dpi}dpi.png"

    # 5. Salva em PNG com transparência e DPI definido
    img.save(output_path, format="PNG", dpi=(dpi, dpi))

    print(f"[✔] Processado e salvo: {output_path}")
    return output_path

def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Remove o fundo de uma imagem e salva como PNG com DPI específico."
    )
    parser.add_argument("input", help="Caminho para a imagem de entrada.")
    parser.add_argument(
        "--dpi", type=int, default=300,
        help="DPI a ser embutido no arquivo PNG de saída (padrão: 300)."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        process_image_to_png(args.input, args.dpi)
    except (FileNotFoundError, IOError) as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)