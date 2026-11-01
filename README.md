# ConnectPlus – API de Comunicados Internos

## Como rodar a aplicação
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

## Contas de demonstração
| Perfil        | Usuário       | Senha      |
|---------------|---------------|------------|
| Administrador | `admin`       | `admin123` |
| Colaborador   | `colaborador` | `colab123` |

## Endpoints
| Método | Rota                  | Acesso        | Resposta |
|--------|-----------------------|---------------|----------|
| POST   | /auth/login           | público       | 200 / 401 |
| GET    | /auth/me              | autenticado   | 200 / 401 |
| POST   | /comunicados          | administrador | 201 / 401 / 403 / 422 |
| GET    | /comunicados          | autenticado   | 200 / 401 |
| GET    | /comunicados/{id}     | autenticado   | 200 / 401 / 404 |
| PUT    | /comunicados/{id}     | administrador | 200 / 401 / 403 / 404 / 422 |
| DELETE | /comunicados/{id}     | administrador | 204 / 401 / 403 / 404 |

## Roteiro de validação no Swagger (cenários 01–10)
1. **01** `POST /auth/login` com admin/admin123 → 200 (ou *Authorize*).
2. **02** `POST /auth/login` com senha errada → 401.
3. **03** Logado como admin, `POST /comunicados` → 201 (autor preenchido automaticamente).
4. **04** *Logout* e *Authorize* como colaborador; `GET /comunicados` → 200.
5. **05** Colaborador `POST /comunicados` → 403.
6. **06** Colaborador `DELETE /comunicados/1` → 403.
7. **07** Sem Authorize (Logout), `GET /comunicados` → 401.
8. **08** Admin `GET /comunicados/9999` → 404.
9. **09** Admin `POST /comunicados` com `"titulo": ""` → 422.
10. **10** Pare o servidor (Ctrl+C), inicie novamente e `GET /comunicados` → o comunicado continua lá (arquivo `connectplus.db`).

## Decisões de segurança
- Autenticação por JWT (Bearer) com expiração de 60 min; senhas guardadas com PBKDF2-SHA256 + salt.
- Nenhum schema de saída expõe senha/hash (RN07).
- Corpo das requisições rejeita campos extras (`extra="forbid"`): enviar `autor_id` ou `perfil` retorna 422 (RN06, RN08).
- Defina `SECRET_KEY` por variável de ambiente fora do ambiente de demonstração.
