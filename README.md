# halfpy — Halftone & Image Tools

Projeto com um conjunto de scripts Python para gerar halftones coloridos, remover fundo, aplicar super-resolução e outras utilidades de imagem.

## Conteúdo principal
- `process.py` — canivete suíço com subcomandos (`check-env`, `remove-bg`, `enhance`, `upscale`, `halftone`, `sharpen`).
- `half.py` — gerador de halftone com camadas semitransparentes (CLI).
- `ai_enhance.py` — upscaling via OpenCV DNN Super-Resolution (edsr/espcn/fsrcnn/lapsrn).
- `upscale.py`, `sharpen.py`, `remove_bg.py` — utilitários adicionais (também acessíveis via `process.py`).
- `models/` e `ai_models/` — modelos pré-treinados (p. ex. EDSR `.pb`).

## Pré-requisitos
- Python 3.8+ (recomendado usar 3.10; o `.venv` padrão foi recriado com essa versão).
- Git (para controle de versão) e Git LFS recomendado para modelos grandes.
- Dependências listadas em `requirements.txt`.

### Instalação (Windows — PowerShell)
1. Criar e ativar ambiente virtual:

```powershell
"C:\Program Files\Python310\python.exe" -m venv .venv   # ajuste o caminho caso use outra versão
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
```

3. (Opcional) Git LFS — recomendado para `.pb` grandes:

```powershell
git lfs install
git lfs track "models/*.pb"
git add .gitattributes
git commit -m "Track models with Git LFS"
```

## Uso — CLI principal (`process.py`)

O `process.py` virou o canivete suíço do projeto. Execute `py process.py --help` para ver os subcomandos disponíveis e use `py process.py <comando> --help` para detalhes opcionais. Ambiente virtual ativo é recomendado para todos os exemplos.

### Subcomandos

| Comando          | Descrição                                                                 | Exemplo                                                                                 |
|------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| `check-env`      | Mostra o Python corrente e valida OpenCV/dnn\_superres                    | `py process.py check-env`                                                               |
| `remove-bg`      | Remove o fundo com `rembg`, preservando DPI configurado                   | `py process.py remove-bg entrada.png --dpi 300`                                         |
| `enhance`        | Super-resolução IA (edsr/espcn/fsrcnn/lapsrn) via OpenCV DNN SR           | `py process.py enhance arte.png -m EDSR -s 4 --models-path models`                      |
| `upscale`        | Redimensionamento tradicional com filtros Pillow                          | `py process.py upscale logo.png -s 2.0 -r lanczos`                                      |
| `upscale -d`     | Redimensiona para dimensões exatas                                        | `py process.py upscale logo.png -d 4096 4096`                                           |
| `halftone`       | Gera retícula colorida com gradiente inclinada (`half.halftone_rotate`)   | `py process.py halftone foto.png -b 12 --angle 45 --background claro --layers 4`        |
| `sharpen`        | Aplica filtro de nitidez simples                                          | `py process.py sharpen foto.png --dpi 300`                                              |

### Detalhes de parâmetros

| Comando                    | Explicação                                                                                                                        | Exemplo completo                                                                                              |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| `process.py halftone`     | Exibe todas as opções de `half.py`: `-b/--block-size`, `--angle`, `--shape`, `--dpi`, `--background`, `--layers` e `-o/--output`. | `py process.py halftone arte.png -o arte_halftone.png -b 14 --angle 30 --shape diamond --background claro`    |
| `process.py enhance`      | Usa `ai_enhance.ai_enhance`, valida `modelo × escala` e permite `--models-path` para apontar onde procurar/baixar os `.pb`.        | `py process.py enhance foto.jpg -m LAPSRN -s 2 --models-path .\models --output foto_lapsrn_x2.png`             |

## Uso direto dos scripts

Se preferir chamar cada utilitário separadamente:

### `half.py`

```powershell
py half.py input.jpg -o output_halftone.png -b 12 --angle 45 --shape circle --dpi 300 --background claro --layers 3
```

### `ai_enhance.py`

```powershell
py ai_enhance.py imagem.jpg -o imagem_upscaled.png -m edsr -s 4 --models-path models
```

### `check_cv2.py`

```powershell
py check_cv2.py
```

### Outros utilitários
- `remove_bg.py`: remove o fundo e entrega PNG com DPI ajustável.
- `sharpen.py`: aplica nitidez básica.
- `upscale.py`: contém tanto o helper `upscale_image` (Pillow) quanto as rotinas de super-resolução com OpenCV caso precise usá-las de forma isolada.

Para consultar as opções de qualquer script:

```powershell
py script_name.py --help
```
```
