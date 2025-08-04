import sys

print("--- Verificando Ambiente Python ---")
print(f"Executável: {sys.executable}")
print(f"Versão: {sys.version}\n")

try:
    import cv2
    print("[✔] Módulo 'cv2' importado com sucesso.")
    print(f"    Versão do OpenCV: {cv2.__version__}")
    print(f"    Localização: {cv2.__file__}\n")

    try:
        from cv2.dnn_superres import DnnSuperResImpl_create
        print("[✔] Módulo 'cv2.dnn_superres' importado com sucesso!")
        print("\n--- Diagnóstico ---")
        print("Parece que a instalação está CORRETA. O problema pode estar na forma como você executa o script 'ai_enhance.py'.")
        print("Tente executar usando o caminho completo do Python:")
        print(f'"{sys.executable}" ai_enhance.py sua_imagem.jpg --model EDSR --scale 4')

    except ImportError:
        print("[✘] ERRO: O módulo 'cv2.dnn_superres' NÃO foi encontrado.")
        print("\n--- Diagnóstico ---")
        print("Isso confirma que a sua instalação do OpenCV não é a versão 'contrib'.")
        print("Por favor, execute o seguinte comando para instalar a versão correta para este Python:")
        print(f'"{sys.executable}" -m pip install --force-reinstall --no-cache-dir opencv-contrib-python')

except ImportError:
    print("[✘] ERRO: O módulo 'cv2' NÃO foi encontrado.")
    print("\n--- Diagnóstico ---")
    print("A biblioteca OpenCV não está instalada para este interpretador Python.")
    print("Por favor, execute o seguinte comando para instalar a versão correta:")
    print(f'"{sys.executable}" -m pip install opencv-contrib-python')