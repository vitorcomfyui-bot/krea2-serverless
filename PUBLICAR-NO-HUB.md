# Publicar no RunPod Hub (só para o dono do repositório)

> Resumo da documentação oficial (docs.runpod.io/hub/publishing-guide). Confira lá se algo mudou.

## 1. Criar o repositório

```powershell
cd krea2-serverless
git init
git add .
git commit -m "Krea 2 Turbo serverless v1.0.0"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/krea2-serverless.git
git push -u origin main
```
(crie antes o repositório vazio em github.com/new, **público**)

## 2. Testar antes de publicar (recomendado)

Crie um endpoint pela **Opção B** do README (GitHub Repo) e mande uma requisição de teste.
Se funcionar ali, o build e o teste do Hub também devem passar.

## 3. Publicar

1. RunPod → **Hub** → **Add your repo** → **Get Started**.
2. Cole a URL do repositório.
3. O assistente confere `.runpod/hub.json`, `.runpod/tests.json`, `Dockerfile`, `handler.py` e `README.md`.
4. Crie um **release** no GitHub (o Hub indexa releases, não commits):
   ```powershell
   gh release create v1.0.0 --title "v1.0.0" --notes "Primeira versão: Krea 2 Turbo fp8"
   ```
   (ou pelo site: Releases → Draft a new release → tag `v1.0.0`)
5. O RunPod faz o build e roda o teste de `tests.json` (status **Pending**).
6. Depois dos testes, o time da RunPod revisa manualmente e publica.

## 4. Atualizar

Mudou algo? Faça commit/push e crie um novo release (`v1.0.1`). O Hub reconstrói em geral em até 1 hora.

## Receita para o publisher

Segundo a documentação do Hub, quem publica recebe uma porcentagem das horas de computação usadas
pelos deploys do seu repositório (de 1% a 7%, conforme o volume), paga em créditos RunPod.
Isso soma ao seu link de indicação (https://runpod.io?ref=z08rfp03), que continua no README.

## Se o teste do Hub falhar

- **Timeout:** o primeiro cold start baixa uma imagem grande; aumente `timeout` em `.runpod/tests.json`.
- **GPU indisponível:** troque `gpuTypeId` em `tests.json` (ex.: `NVIDIA L4`, `NVIDIA RTX A5000`).
- **Modelo não encontrado:** os nomes em `models.txt` precisam bater com o workflow.
- **Erro no handler:** o `Dockerfile` renomeia o handler oficial para `/comfy_handler.py`;
  se uma versão nova da imagem base mudar esse arquivo, fixe a tag `5.10.0-base`.
