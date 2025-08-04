#!/usr/bin/env python
# Script de super-resolução IA com OpenCV dnn_superres
#
# 1. Instale dependências:
#    py -m pip install opencv-contrib-python requests tqdm
#
# 2. Execute:
#    py ai_enhance.py "caminho/para/imagem.jpg" -m EDSR -s 4
#
# Modelos válidos (e escalas suportadas):
#   EDSR   : 2, 3, 4
#   FSRCNN : 2, 3, 4
#   ESPCN  : 2, 3, 4
#   LapSRN : 2, 4, 8
#
# Os pesos são baixados de:
# https://github.com/opencv/opencv_extra/tree/master/testdata/dnn

import sys
import os
import argparse
import cv2
import requests
from tqdm import tqdm

try:
    from cv2.dnn_superres import DnnSuperResImpl_create
except ImportError:
    print("[✖] ERRO: Módulo 'dnn_superres' não encontrado.", file=sys.stderr)
    print("      Sua instalação do OpenCV pode não ser a versão 'contrib'.", file=sys.stderr)
    print("      Execute 'py check_cv2.py' para diagnosticar ou instale a versão correta com:", file=sys.stderr)
    print(f'      "{sys.executable}" -m pip install --force-reinstall opencv-contrib-python', file=sys.stderr)
    sys.exit(1)

# Diretório para armazenar os modelos de IA baixados
MODELS_DIR = "ai_models"

# Definições de modelos e escalas
VALID_MODELS = {
    'EDSR':   [2, 3, 4],
    'FSRCNN': [2, 3, 4],
    'ESPCN':  [2, 3, 4],
    'LAPSRN': [2, 4, 8],
}
# Mapeia chave para prefixo de arquivo exato (case-sensitive)
MODEL_FILENAMES = {
    'EDSR':   'EDSR',
    'FSRCNN': 'FSRCNN',
    'ESPCN':  'ESPCN',
    'LAPSRN': 'LapSRN',
}

def download_model(model_path: str, model_url: str):
    """Baixa o arquivo de modelo com uma barra de progresso se não existir localmente."""
    # Garante que o diretório de modelos exista
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        model_filename = os.path.basename(model_path)
        print(f"[→] Baixando {model_filename} para '{MODELS_DIR}/'…")
        try:
            resp = requests.get(model_url, stream=True)
            resp.raise_for_status()

            total_size = int(resp.headers.get('content-length', 0))
            block_size = 8192  # 8KB

            with open(model_path, 'wb') as f, tqdm(
                desc=model_filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in resp.iter_content(block_size):
                    bar.update(len(chunk))
                    f.write(chunk)

            print(f"[✔] Modelo salvo em: {model_path}")
        except requests.exceptions.RequestException as e:
            print(f"\n[✖] Erro de download: {e}", file=sys.stderr)
            # Remove arquivo parcial se o download falhar
            if os.path.exists(model_path):
                os.remove(model_path)
            sys.exit(1)

def ai_enhance(input_path: str, model: str, scale: int, models_path: str = None) -> str:
    """
    Aplica super-resolução IA e salva PNG resultante. Retorna o caminho de saída.
    Prioriza modelos de um caminho local, se fornecido.
    """
    key = model.upper()
    if key not in VALID_MODELS or scale not in VALID_MODELS[key]:
        raise ValueError(f"'{model}' não suporta escala x{scale}.")

    file_prefix = MODEL_FILENAMES[key]
    model_name = f"{file_prefix}_x{scale}.pb"
    final_model_path = None

    # 1. Tenta encontrar o modelo no caminho local fornecido pelo usuário
    if models_path and os.path.isdir(models_path):
        potential_path = os.path.join(models_path, model_name)
        if os.path.exists(potential_path):
            print(f"[i] Usando modelo local encontrado em: {potential_path}")
            final_model_path = potential_path

    # 2. Se não encontrou, usa o caminho padrão e baixa se necessário
    if not final_model_path:
        default_model_path = os.path.join(MODELS_DIR, model_name)
        model_url = f"https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/{model_name}"
        download_model(default_model_path, model_url)
        final_model_path = default_model_path

    print(f"[i] Carregando imagem: {input_path}")
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Falha ao abrir '{input_path}'. O arquivo pode não existir ou estar corrompido.")

    h, w = img.shape[:2] # Usar [:2] para compatibilidade com imagens em escala de cinza
    total_px = (w*scale)*(h*scale)
    if total_px > 256*1024*1024:
        print(f"[⚠] Saída grande: {w*scale}×{h*scale} pixels — cuidado com RAM.")

    try:
        sr = DnnSuperResImpl_create()
        sr.readModel(final_model_path)
        sr.setModel(file_prefix.lower(), scale)

        print(f"[i] Aplicando {file_prefix} x{scale}… (isso pode levar um tempo)")
        result = sr.upsample(img)

        base, _ = os.path.splitext(input_path)
        out_path = f"{base}_AI_{file_prefix}x{scale}.png"
        cv2.imwrite(out_path, result)
        print(f"[✔] Salvo em: {out_path}")
        return out_path

    except cv2.error as e:
        raise RuntimeError(f"Erro do OpenCV durante o processamento: {e}. O modelo pode estar corrompido.") from e

def parse_args():
    p = argparse.ArgumentParser(description="Super-resolução IA com OpenCV")
    p.add_argument("input", help="Imagem de entrada (JPG, PNG etc.)")
    p.add_argument("-m","--model", type=str.upper, choices=VALID_MODELS.keys(),
                   default="EDSR",help="Modelo: EDSR, FSRCNN, ESPCN, LAPSRN (não diferencia maiúsculas/minúsculas).")
    p.add_argument("-s","--scale",type=int,default=4,
                   help="Escala: 2,3,4 (8 apenas para LapSRN)")
    p.add_argument("--models-path", help="Caminho para a pasta com modelos .pb locais, evitando o download.")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        ai_enhance(args.input, args.model, args.scale, args.models_path)
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"[✖] ERRO: {e}", file=sys.stderr)
        sys.exit(1)
