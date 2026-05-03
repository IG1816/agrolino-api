# Agrolino API

Backend FastAPI + PostgreSQL (async) para o site Agrolino. Mesma origem em produção: `https://agrolino.com.br/api/...` atrás de Nginx/Caddy; o front em `/` usa `fetch(..., { credentials: "include" })`.

## Requisitos

- Python 3.11+
- PostgreSQL 15+

## Setup local

```powershell
cd C:\Users\user\.cursor\agrolino-api
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Ajuste `DATABASE_URL` no `.env`. Para Alembic, a URL síncrona é derivada automaticamente removendo `+asyncpg` (ou defina `DATABASE_URL_SYNC`).

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: `http://127.0.0.1:8000/api/v1/...`
- Docs: `http://127.0.0.1:8000/api/docs`
- OpenAPI: `http://127.0.0.1:8000/api/openapi.json`

## Rotas MVP

| Método | Caminho | Auth |
|--------|---------|------|
| GET | `/api/v1/health` | Não |
| GET | `/api/v1/ready` | Não |
| GET | `/api/v1/products` | Não |
| GET | `/api/v1/products/{slug}` | Não |
| POST | `/api/v1/auth/register` | Não |
| POST | `/api/v1/auth/login` | Não (define cookie de sessão) |
| POST | `/api/v1/auth/logout` | Não (limpa cookie) |
| GET | `/api/v1/me` | Sim |
| PATCH | `/api/v1/me` | Sim |

JSON de resposta usa **camelCase** (alias Pydantic) onde aplicável (ex.: `priceCents`, `pageSize`).

## Segurança (estado atual)

- Senha: Argon2id; cookie de sessão `HttpOnly`, `SameSite` configurável (padrão `strict`), `Secure` conforme `SESSION_COOKIE_SECURE`.
- **CSRF:** ainda não há token dedicado; com `SameSite=Strict` e mesma origem o risco clássico cai muito — próximo passo recomendado é token CSRF em mutações.

## Próximos passos sugeridos

- Rate limit no edge (Caddy/Nginx) ou middleware para login/registro.
- CRUD admin de produtos + auditoria em writes.
- Seeds de desenvolvimento (`scripts/seed.py`).
