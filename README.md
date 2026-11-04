# Krea 2 Turbo — RunPod Serverless

Gerador de imagens **Krea 2 Turbo (fp8)** como API, rodando no **RunPod Serverless**:
você paga só pelos segundos de GPU usados e o endpoint desliga sozinho quando fica parado.

Usado pelo projeto **Reels Explicativo** para gerar os fundos dos vídeos, mas serve para qualquer automação
(carrosséis, thumbnails, n8n, Make, Python…).

> Ainda não tem conta no RunPod? Crie pelo link: **https://runpod.io?ref=z08rfp03**

---

## Passo a passo: criar o endpoint

### Opção A — RunPod Hub (1 clique, sem build)

1. Entre no RunPod → menu **Hub** → procure **Krea 2 Turbo — Text to Image**.
2. Clique em **Deploy** → **Create Endpoint**.
3. Ajuste as configurações (veja a tabela abaixo) e confirme.
4. Espere o status ficar **Ready** (alguns minutos na primeira vez).

### Opção B — Direto do GitHub (se ainda não estiver no Hub)

1. Faça um **fork** deste repositório na sua conta do GitHub.
2. RunPod → **Serverless** → **New Endpoint** → **GitHub Repo**.
3. Conecte sua conta do GitHub e escolha o fork, branch `main`.
4. **Dockerfile Path:** `Dockerfile` · **Build Context:** `.` (raiz).
5. Ajuste as configurações abaixo e clique em **Create Endpoint**.
6. O RunPod faz o build nos servidores dele (pode levar de 20 a 40 min na primeira vez — a imagem tem os modelos dentro).

### Configurações recomendadas

| Campo | Valor | Por quê |
|---|---|---|
| GPU | 24 GB (RTX 4090 / L4 / A5000) | o modelo fp8 cabe com folga |
| Active Workers | **0** | não paga nada parado |
| Max Workers | **3** | gera várias imagens em paralelo |
| Idle Timeout | **5 s** | desliga logo depois de terminar |
| FlashBoot | **ligado** | acelera os próximos cold starts |
| Execution Timeout | 600 s | margem para o primeiro cold start |

### Pegar as credenciais

1. **Endpoint ID:** na página do endpoint, abaixo do nome (ex.: `abc123xyz`).
2. **API Key:** RunPod → **Settings** → **API Keys** → **Create API Key** (permissão de leitura e escrita).

No projeto Reels Explicativo, coloque no `.env`:
```
RUNPOD_API_KEY=sua_chave
RUNPOD_ENDPOINT_ID=seu_endpoint_id
```
e teste com `npm run teste-imagem`.

---

## Como usar a API

### Modo simples (só o prompt)

```bash
curl -X POST https://api.runpod.ai/v2/SEU_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "cinematic photo of a gym at night, dramatic light", "width": 1024, "height": 1792, "seed": 42}}'
```

| Campo | Padrão | Limites |
|---|---|---|
| `prompt` | — (obrigatório) | |
| `negative_prompt` | o do workflow | |
| `width`, `height` | 1024 × 1792 | 256–2048, múltiplos de 16 |
| `seed` | aleatório | |
| `steps` | 12 | 1–50 |

### Modo workflow (ComfyUI completo)

Envie `{"input": {"workflow": { ...workflow em formato API... }}}` — os nomes dos modelos devem ser
`krea2_turbo_fp8_scaled.safetensors`, `qwen3vl_4b_fp8_scaled.safetensors` e `qwen_image_vae.safetensors`.

### Resposta

```json
{ "status": "COMPLETED", "output": { "images": [ { "filename": "...png", "type": "base64", "data": "iVBORw0..." } ] } }
```

Para jobs longos use `/run` (devolve um `id`) e consulte `/status/<id>`. Python:

```python
import base64, requests
r = requests.post(f"https://api.runpod.ai/v2/{EP}/runsync",
                  headers={"Authorization": f"Bearer {KEY}"},
                  json={"input": {"prompt": "a dark gym, cinematic"}}, timeout=600).json()
open("img.png", "wb").write(base64.b64decode(r["output"]["images"][0]["data"]))
```

---

## O que tem dentro

| Arquivo | Função |
|---|---|
| `Dockerfile` | parte de `runpod/worker-comfyui:5.10.0-base`, baixa os modelos e instala o handler |
| `models.txt` | URLs dos modelos (Comfy-Org / HuggingFace) |
| `nodes.txt` | custom nodes do ComfyUI (vazio por padrão) |
| `handler.py` | aceita `prompt` simples e delega ao handler oficial do worker-comfyui |
| `workflow_krea2_api.json` | workflow Krea 2 Turbo (12 passos, euler/beta) |
| `.runpod/hub.json`, `.runpod/tests.json` | configuração do RunPod Hub |

Licença dos modelos: confira os termos do Krea 2 e do Qwen no HuggingFace antes de uso comercial.
