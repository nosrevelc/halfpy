# ai_enhance_opencv.py
# Script para aprimoramento de imagem usando OpenCV DNN Super-Resolution
# Suporta Python 3.12
# Requisitos:
#   pip install opencv-contrib-python

import argparse
import os
import urllib.request
import cv2
from cv2.dnn_superres import DnnSuperResImpl_create

def download_model(model_name: str, scale: int, model_dir: str = "models") -> str:
    """
    Baixa o arquivo .pb do modelo SR se não existir.
    Os modelos estão no repositório oficial do OpenCV Contrib.
    """
    filename = f"{model_name.upper()}_x{scale}.pb"
    path = os.path.join(model_dir, filename)
    if not os.path.exists(path):
        os.makedirs(model_dir, exist_ok=True)
        url = f"https://github.com/opencv/opencv_contrib/raw/master/modules/dnn_superres/samples/{filename}"
        print(f"Baixando modelo {filename}...")
        urllib.request.urlretrieve(url, path)
    return path


def enhance_image(input_path: str, output_path: str, model_name: str = "edsr", scale: int = 4):
    """
    Carrega a imagem, aplica super-resolução com OpenCV e salva o resultado.
    """
    model_path = download_model(model_name, scale)
    sr = DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel(model_name, scale)

    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Não foi possível abrir a imagem: {input_path}")

    import time
    print(f"Aprimorando imagem: {input_path} (modelo: {model_name}, scale x{scale})...")
    t0 = time.time()
    result = sr.upsample(img)
    print(f"🕒 tempo de upsample: {time.time()-t0:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="AI Image Enhancement com OpenCV DNN Super-Resolution")
    parser.add_argument('input', help='Caminho para a imagem de entrada')
    parser.add_argument('-o', '--output', default=None, help='Caminho de saída (padrão: input_enhanced.png)')
    parser.add_argument('-m', '--model', choices=['edsr', 'espcn', 'fsrcnn', 'lapsrn'], default='edsr',
                        help='Modelo de super-resolução (edsr, espcn, fsrcnn, lapsrn)')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 3, 4], default=4,
                        help='Fator de upscaling (2, 3 ou 4)')
    args = parser.parse_args()

    input_path = args.input
    base, ext = os.path.splitext(input_path)
    output_path = args.output or f"{base}_enhanced_{args.model}_x{args.scale}.png"

    enhance_image(input_path, output_path, model_name=args.model, scale=args.scale)

if __name__ == '__main__':
    main()
