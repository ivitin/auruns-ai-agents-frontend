# Como Rodar

## 1. Backend

```bash
cd /home/victor/Desktop/auruns-ai-agent/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

> Na primeira vez (ou após deletar `chroma_db/`), aguarde a indexação dos equipamentos antes de usar o chat.

## 2. Frontend

Abra um novo terminal:

```bash
cd /home/victor/Desktop/auruns-ai-agent/frontend
python3 -m http.server 8080
```

## 3. Acessar

Abra o browser em: **http://localhost:8080**

---

## Reindexar equipamentos manualmente

```bash
curl -X POST http://localhost:8000/api/v1/admin/refresh
```

## Parar os servidores

`Ctrl+C` em cada terminal.
