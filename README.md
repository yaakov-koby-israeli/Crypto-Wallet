# Crypto Wallet

Full-stack crypto wallet that pairs a FastAPI backend (JWT auth, SQLAlchemy, Web3.py) with a React + Vite frontend (Tailwind UI). User/account data lives in SQLite while balances and transfers run against a local Ganache chain.

## Stack
- FastAPI, Pydantic, SQLAlchemy, OAuth2/JWT (python-jose), passlib[bcrypt]
- Web3.py against Ganache for balance reads, ETH transfers, and transaction history
- React 18 + Vite, Tailwind CSS, axios; JWT persisted in `localStorage`

## Project layout
Backend
- `main.py` - local dev entry (Uvicorn)
- `app/app.py` - FastAPI app, CORS, router registration, DB bootstrap
- `app/configuration/config.py` - Pydantic settings from `.env`
- `app/database/db_config.py` / `app/database/models.py` - engine/session/Base and `Users`/`Account` tables
- `routers/auth.py` - register + token issuing; `routers/users.py` - account setup, transfers, history; `routers/admin.py` - admin-only listings/deletes
- `app/service/*` - Ganache client (`web3_service.py`), account creation/balance sync, user lookup
- `dependencies/*` - shared DB + auth dependencies
- `app/schemas/*` - request/response models (CreateUserRequest, Token, TransferRequest)
Frontend
- `frontend/src/App.jsx` - routing + theme toggle
- `frontend/src/controllers/useAuth.js` / `useWallet.js` - auth state, wallet calls, transactions
- `frontend/src/api/walletService.js` - axios client for backend endpoints
- Views: `frontend/src/views/Login.jsx`, `Register.jsx`, `Dashboard.jsx`
- UI: `frontend/src/components/ui/Components.jsx`, Tailwind theme in `frontend/tailwind.config.js`

## Prerequisites
- Python 3.11+
- Node.js 20+
- Ganache running locally (default RPC http://127.0.0.1:7545, CHAIN_ID=1337) with funded accounts
- pip and npm available; SQLite is bundled with Python

## Backend setup
1) Create a virtualenv and install deps:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose[cryptography] pydantic-settings web3 python-multipart
```
2) Add a `.env` in the repo root:
```
DATABASE_URL=sqlite:///./cryptowallet.db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GANACHE_URL=http://127.0.0.1:7545
CHAIN_ID=1337
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```
3) Start the API: `uvicorn app.app:app --reload` (or `python main.py`). Tables are created automatically on startup.

## Frontend setup
1) `cd frontend`
2) `npm install`
3) Create `.env` with `VITE_API_BASE_URL=http://localhost:8000`
4) Run `npm run dev` (Vite defaults to http://localhost:5173). Ensure the origin is included in `CORS_ORIGINS`.

## Auth and usage flow
1) Register: `POST /auth` with JSON `{ username, email, first_name, last_name, password, role }` (role is forced to `user` server-side). Public key is not required at signup; add it later during account setup. Passwords are bcrypt-hashed.
2) Login: `POST /auth/token` (form fields `username`, `password`) -> `{ access_token, token_type, public_key }`. Send `Authorization: Bearer <token>` on protected routes.
3) Set up account (auth): `POST /user/set-up-account?public_key=0x...` validates the Ganache address, saves it on the user, creates an `Account` row if missing, and syncs on-chain balance.
4) Transfer ETH (auth): `POST /user/transfer-eth` with `{ "to_account": int, "amount": float }` submits an on-chain tx and refreshes both accounts' balances; returns the transaction hash.
5) Transactions (auth): `GET /user/user-transactions` returns on-chain history for the caller's public key.
6) Delete account (auth): `DELETE /user/delete-account` removes the caller's account.
7) Admin only (requires `role=admin`): `GET /admin/users`, `GET /admin/accounts`, `DELETE /admin/delete-user/{user_id}`. Promote users to admin directly in the DB if needed.

### Quick cURL examples
Register:
```
curl -X POST http://localhost:8000/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","first_name":"Alice","last_name":"Doe","password":"secret","role":"user"}'
```
Login:
```
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret"
```
Transfer (with token):
```
curl -X POST http://localhost:8000/user/transfer-eth \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"to_account":2,"amount":0.1}'
```

## Frontend behavior
- Login/Register pages issue auth calls and persist the JWT in `localStorage` (`token` key)
- Dashboard syncs a Ganache public key, shows balance/account id, sends ETH by account id, and lists on-chain transactions
- Includes a dark/light theme toggle persisted to `localStorage`

## Notes
- Ganache must be running and the supplied public keys must exist and be funded there
- Default DB is `cryptowallet.db` in the repo root; adjust `DATABASE_URL` for another DB engine
