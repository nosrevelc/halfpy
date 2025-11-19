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

VALID_MODELS = {
    "EDSR": [2, 3, 4],
    "ESPCN": [2, 3, 4],
    "FSRCNN": [2, 3, 4],
    "LAPSRN": [2, 3, 4],
}

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


def enhance_image(
    input_path: str,
    output_path: str,
    model_name: str = "edsr",
    scale: int = 4,
    model_dir: str = "models"
) -> str:
    """
    Carrega a imagem, aplica super-resolução com OpenCV e salva o resultado.
    """
    model_path = download_model(model_name, scale, model_dir=model_dir)
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
    print(f"[tempo] upsample: {time.time()-t0:.1f}s")

    cv2.imwrite(output_path, result)
    print(f"[OK] Arquivo salvo em: {output_path}")
    return output_path


def ai_enhance(
    input_path: str,
    model: str,
    scale: int,
    models_path: str | None = None,
    output_path: str | None = None,
) -> str:
    """
    Wrapper compatível com o process.py.
    """
    model_upper = model.upper()
    if model_upper not in VALID_MODELS:
        raise ValueError(f"Modelo '{model}' não suportado. Opções: {list(VALID_MODELS)}")
    if scale not in VALID_MODELS[model_upper]:
        raise ValueError(
            f"Modelo '{model_upper}' não suporta a escala x{scale}. "
            f"Opções válidas: {VALID_MODELS[model_upper]}"
        )
    base, _ = os.path.splitext(input_path)
    model_slug = model.lower()
    out_path = output_path or f"{base}_enhanced_{model_slug}_x{scale}.png"
    return enhance_image(
        input_path,
        out_path,
        model_name=model_slug,
        scale=scale,
        model_dir=models_path or "models",
    )


def main():
    parser = argparse.ArgumentParser(description="AI Image Enhancement com OpenCV DNN Super-Resolution")
    parser.add_argument('input', help='Caminho para a imagem de entrada')
    parser.add_argument('-o', '--output', default=None, help='Caminho de saída (padrão: input_enhanced.png)')
    parser.add_argument('-m', '--model', choices=[m.lower() for m in VALID_MODELS], default='edsr',
                        help='Modelo de super-resolução (edsr, espcn, fsrcnn, lapsrn)')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 3, 4], default=4,
                        help='Fator de upscaling (2, 3 ou 4)')
    parser.add_argument('--models-path', default="models", help='Pasta para armazenar/usar arquivos .pb')
    args = parser.parse_args()

    input_path = args.input
    base, ext = os.path.splitext(input_path)
    output_path = args.output or f"{base}_enhanced_{args.model}_x{args.scale}.png"

    enhance_image(
        input_path,
        output_path,
        model_name=args.model,
        scale=args.scale,
        model_dir=args.models_path,
    )

if __name__ == '__main__':
    main()
