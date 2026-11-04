"""
Handler do Krea 2 Serverless.

Aceita dois formatos de entrada:

1) Simples (recomendado):
   {"input": {"prompt": "...", "width": 1024, "height": 1792, "seed": 42, "steps": 12}}

2) Workflow ComfyUI completo (formato API) — compatível com o worker-comfyui oficial:
   {"input": {"workflow": {...}}}

Em ambos os casos a resposta é a do worker-comfyui:
   {"images": [{"filename": "...", "type": "base64", "data": "..."}]}
"""
import copy
import inspect
import json
import random
from pathlib import Path

import runpod

import comfy_handler  # handler original do runpod/worker-comfyui (renomeado no Dockerfile)

WORKFLOW = json.loads((Path(__file__).parent / "workflow_krea2_api.json").read_text(encoding="utf-8"))

# nós do workflow_krea2_api.json
NO_PROMPT, NO_NEGATIVO, NO_SAMPLER, NO_LATENTE = "52", "63", "61", "73"

LIMITES = {"width": (256, 2048), "height": (256, 2048), "steps": (1, 50)}


def _int(valor, nome, padrao):
    try:
        v = int(valor if valor is not None else padrao)
    except (TypeError, ValueError):
        v = padrao
    lo, hi = LIMITES.get(nome, (v, v))
    v = max(lo, min(hi, v))
    return v - v % 16 if nome in ("width", "height") else v


def montar_workflow(entrada: dict) -> dict:
    wf = copy.deepcopy(WORKFLOW)
    wf[NO_PROMPT]["inputs"]["text"] = str(entrada["prompt"])
    if entrada.get("negative_prompt") is not None:
        wf[NO_NEGATIVO]["inputs"]["text"] = str(entrada["negative_prompt"])
    s = wf[NO_SAMPLER]["inputs"]
    s["seed"] = int(entrada.get("seed") or random.randint(1, 2**48))
    s["steps"] = _int(entrada.get("steps"), "steps", s["steps"])
    lat = wf[NO_LATENTE]["inputs"]
    lat["width"] = _int(entrada.get("width"), "width", lat["width"])
    lat["height"] = _int(entrada.get("height"), "height", lat["height"])
    lat["batch_size"] = 1
    return wf


def handler(job):
    entrada = job.get("input") or {}
    if "workflow" not in entrada:
        if not entrada.get("prompt"):
            return {"error": "Envie 'prompt' (modo simples) ou 'workflow' (formato API do ComfyUI)."}
        job = {**job, "input": {"workflow": montar_workflow(entrada)}}
    resultado = comfy_handler.handler(job)
    if inspect.isgenerator(resultado):  # compatibilidade caso o handler original seja gerador
        ultimo = None
        for ultimo in resultado:
            pass
        resultado = ultimo
    return resultado


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
