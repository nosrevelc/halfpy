# halfpy — Halftone & Image Tools

Projeto com um conjunto de scripts Python para gerar halftones coloridos, remover fundo, aplicar super-resolução e outras utilidades de imagem.

## Conteúdo principal
- `half.py` — gerador de halftone com camadas semitransparentes (CLI).
- `ai_enhance.py` — upscaling via OpenCV DNN Super-Resolution (edsr/espcn/fsrcnn/lapsrn).
- `upscale.py`, `sharpen.py`, `remove_bg.py`, `process.py` — utilitários adicionais.
- `models/` e `ai_models/` — modelos pré-treinados (p. ex. EDSR `.pb`).

## Pré-requisitos
- Python 3.8+ (testado com 3.10/3.12).
- Git (para controle de versão) e Git LFS recomendado para modelos grandes.
- Dependências listadas em `requirements.txt`.

### Instalação (Windows — PowerShell)
1. Criar e ativar ambiente virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
py -m pip install -r requirements.txt
# Se for usar o ai_enhance com OpenCV DNN SR
py -m pip install opencv-contrib-python
```

3. (Opcional) Git LFS — recomendado para `.pb` grandes:

```powershell
git lfs install
git lfs track "models/*.pb"
git add .gitattributes
git commit -m "Track models with Git LFS"
```

## Uso — exemplos de CLI

Observação: todos os exemplos abaixo assumem que você está no diretório do projeto e que o ambiente virtual está ativado.

### 1) Gerar Halftone (`half.py`)

Opções principais (algumas):
- `input` (posicional): caminho da imagem de entrada.
- `-o, --output`: caminho do PNG de saída.
- `-b, --block-size` (int): tamanho do bloco/ponto (padrão: 10).
- `--angle` (float): ângulo em graus (padrão: 45).
- `--shape`: `circle|square|diamond` (padrão: circle).
- `--dpi` (int): DPI do PNG de saída (padrão: 300).
- `--background`: `claro|escuro` (quando omisso, o script pode perguntar).
- `--layers` (int): número de camadas semitransparentes (padrão: 3).

Exemplo:

```powershell
py half.py input.jpg -o output_halftone.png -b 12 --angle 45 --shape circle --dpi 300 --background claro --layers 3
```

Também existe um `halftone.bat` para executar o processo no Windows de forma direta.

### 2) AI Image Enhancement (`ai_enhance.py`)

Opções:
- `input` (posicional): caminho da imagem de entrada
- `-o, --output`: arquivo de saída (padrão: `<input>_enhanced_<model>_x<scale>.png`)
- `-m, --model`: `edsr|espcn|fsrcnn|lapsrn` (padrão: edsr)
- `-s, --scale`: `2|3|4` (padrão: 4)

Exemplos:

```powershell
py ai_enhance.py imagem.jpg -o imagem_upscaled.png -m edsr -s 4
py ai_enhance.py foto.png --model fsrcnn --scale 2
```

Se o modelo não existir em `models/` ele pode ser baixado automaticamente (dependendo do script), ou você pode colocar os `.pb` em `models/` manualmente.

### 3) Verificar OpenCV (`check_cv2.py`)

Use este script para checar se o OpenCV está disponível e se o módulo DNN/SR funciona:

```powershell
py check_cv2.py
```

### 4) Outros scripts
- `remove_bg.py`: remover background de imagens (ver parâmetros no topo do arquivo).
- `upscale.py` / `sharpen.py` / `process.py`: utilitários auxiliares — veja `--help` ou o topo do script.

Para ver as opções exatas de qualquer script Python, use:

```powershell
py script_name.py --help
```
```