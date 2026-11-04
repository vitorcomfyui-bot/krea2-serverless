# Krea 2 Turbo — RunPod Serverless (compatível com RunPod Hub)
# Base oficial: ComfyUI + start.sh + handler da RunPod
FROM runpod/worker-comfyui:5.10.0-base

# Custom nodes (um por linha em nodes.txt; vazio = nenhum)
COPY nodes.txt /tmp/nodes.txt
RUN tr -d '\r' < /tmp/nodes.txt | grep -v '^\s*\(#\|$\)' > /tmp/nodes.clean || true; \
    if [ -s /tmp/nodes.clean ]; then xargs -r -a /tmp/nodes.clean comfy-node-install; fi

# Modelos baixados no build (ficam dentro da imagem = cold start rápido, sem Network Volume)
COPY models.txt /tmp/models.txt
COPY baixar_modelos.sh /tmp/baixar_modelos.sh
RUN tr -d '\r' < /tmp/baixar_modelos.sh > /tmp/b.sh && bash /tmp/b.sh /tmp/models.txt && rm -f /tmp/models.txt /tmp/b.sh

# Handler próprio (aceita "prompt" simples) por cima do handler original
RUN test -f /handler.py && mv /handler.py /comfy_handler.py
COPY handler.py /handler.py
COPY workflow_krea2_api.json /workflow_krea2_api.json
