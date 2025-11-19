# ai_enhance_opencv.py
# Script para aprimoramento de imagem usando OpenCV DNN Super-Resolution
# Compatível com Python 3.12
# Requisitos:
#   pip install opencv-contrib-python

import argparse
import os
import cv2
from cv2.dnn_superres import DnnSuperResImpl_create
from PIL import Image

def upscale_image(
    input_path: str,
    scale_factor: float | None = None,
    target_width: int | None = None,
    target_height: int | None = None,
    resample_filter=Image.Resampling.LANCZOS,
    output_path: str | None = None,
) -> str:
    """
    Redimensiona uma imagem usando Pillow, mantendo a proporção quando o fator é usado.
    """
    if scale_factor is None and (target_width is None or target_height is None):
        raise ValueError("Informe scale_factor ou (target_width e target_height).")

    img = Image.open(input_path)
    if scale_factor is not None:
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    else:
        new_size = (target_width, target_height)

    resized = img.resize(new_size, resample=resample_filter)
    base, _ = os.path.splitext(input_path)
    out = output_path or f"{base}_upscaled.png"
    resized.save(out, format="PNG", dpi=img.info.get("dpi", (300, 300)))
    print(f"[OK] Imagem redimensionada salva em: {out}")
    return out


def get_local_model_path(model_name: str, scale: int, model_dir: str) -> str:
    """
    Verifica se o modelo existe localmente em model_dir.
    Retorna o caminho se existir, caso contrário retorna string vazia.
    """
    filename = f"{model_name.upper()}_x{scale}.pb"
    local_path = os.path.join(model_dir, filename)
    if os.path.isfile(local_path):
        return local_path
    return ''


def download_model(model_name: str, scale: int, model_dir: str = "models") -> str:
    """
    Baixa o arquivo .pb do modelo SR se não existir localmente.
    Usa repositório OpenCV Contrib.
    """
    os.makedirs(model_dir, exist_ok=True)
    filename = f"{model_name.upper()}_x{scale}.pb"
    path = os.path.join(model_dir, filename)
    if not os.path.isfile(path):
        url = f"https://github.com/opencv/opencv_contrib/raw/master/modules/dnn_superres/samples/{filename}"
        print(f"Modelo não encontrado localmente. Tentando baixar de: {url}")
        try:
            import urllib.request
            urllib.request.urlretrieve(url, path)
            print(f"Download concluído: {path}")
        except Exception as e:
            raise RuntimeError(f"Falha ao baixar o modelo: {e}\n"
                                "Verifique sua conexão ou coloque o arquivo manualmente em '{model_dir}'.")
    else:
        print(f"Usando modelo local: {path}")
    return path


def enhance_image(input_path: str, output_path: str, model_name: str = "edsr", scale: int = 4, model_dir: str = "models"):
    """
    Aplica super-resolução com OpenCV e salva o resultado.
    """
    # Se houver modelo local, use-o; senão baixe
    local = get_local_model_path(model_name, scale, model_dir)
    model_path = local or download_model(model_name, scale, model_dir)

    sr = DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel(model_name, scale)

    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Não foi possível abrir a imagem: {input_path}")

    print(f"Aprimorando imagem: {input_path} (modelo: {model_name}, scale x{scale})...")
    result = sr.upsample(img)
    cv2.imwrite(output_path, result)
    print(f"Imagem aprimorada salva em: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="AI Image Enhancement com OpenCV DNN Super-Resolution")
    parser.add_argument('input', help='Caminho para a imagem de entrada')
    parser.add_argument('-o', '--output', default=None,
                        help='Caminho de saída (padrão: input_enhanced.png)')
    parser.add_argument('-m', '--model', choices=['edsr', 'espcn', 'fsrcnn', 'lapsrn'], default='edsr',
                        help='Modelo de super-resolução (edsr, espcn, fsrcnn, lapsrn)')
    parser.add_argument('-s', '--scale', type=int, choices=[2, 3, 4], default=4,
                        help='Fator de upscaling (2, 3 ou 4)')
    parser.add_argument('-d', '--model_dir', default='models',
                        help='Diretório onde ficam os modelos .pb')
    args = parser.parse_args()

    input_path = args.input
    base, ext = os.path.splitext(input_path)
    output_path = args.output or f"{base}_enhanced_{args.model}_x{args.scale}{ext}"

    enhance_image(
        input_path,
        output_path,
        model_name=args.model,
        scale=args.scale,
        model_dir=args.model_dir
    )

if __name__ == '__main__':
    main()
