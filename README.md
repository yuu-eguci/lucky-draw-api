RESTful API for Lucky Draw
===

抽選アプリ (cshimegi/lucky-draw-gui) で使う参加者 (attendee) を登録・取得・更新・削除する API です。

- Docker: 対応!
- Python: 3.14!
- Linter: Ruff!
- Test: Django test runner (unittest) + DRF APIClient!
- Django: 5.2 (LTS)!
- Django REST framework: 3.18!

## パッと実行してみたい

```bash
docker compose up --build
# 別のターミナルで
curl -X POST http://localhost:8080/api/v1/attendee/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "taro", "email": "taro@example.com", "phone": "09012345"}'
curl http://localhost:8080/api/v1/attendee/
```

- コンテナ起動時に migrate してから開発サーバを `localhost:8080` で立ち上げます
- データは Docker volume (`lucky-draw-data`) の SQLite に保存されます
- ブラウザで `http://localhost:8080/api/v1/` を開くと DRF の画面で API を試せます
- 開発用の設定です。認証はないので、インターネットに公開しないでください

## API

| メソッド | パス | 内容 |
|---|---|---|
| GET | `/api/v1/attendee/` | 一覧 |
| POST | `/api/v1/attendee/` | 登録 |
| GET | `/api/v1/attendee/{id}/` | 1件取得 |
| PUT / PATCH | `/api/v1/attendee/{id}/` | 更新 |
| DELETE | `/api/v1/attendee/{id}/` | 削除 |

```bash
curl http://localhost:8080/api/v1/attendee/1/
curl -X PUT http://localhost:8080/api/v1/attendee/1/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "taro", "email": "taro@example.com", "phone": "0901234567"}'
curl -X PATCH http://localhost:8080/api/v1/attendee/1/ \
  -H 'Content-Type: application/json' -d '{"name": "jiro"}'
curl -X DELETE http://localhost:8080/api/v1/attendee/1/
```

- 末尾の `/` は必須です
- `curl http://localhost:8080/api/v1/` でエンドポイント一覧 (JSON) が返ります
- 入力エラーは 400 で `{"phone": ["..."]}` のような JSON が返ります
- `name`: 1-64 文字 (日本語も可)
- `email`: メールアドレス、重複不可
- `phone`: 8-10 文字の英数字・`-`・`_`、重複不可
- 同じ API は昔からの `/admin/attendee/` でも呼べます

## 設定 (環境変数)

| 変数 | 既定値 | 内容 |
|---|---|---|
| `DJANGO_DEBUG` | `0` (compose では `1`) | `1` で DEBUG |
| `DJANGO_SECRET_KEY` | DEBUG 時だけ開発用の値 | DEBUG でないときは必須 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | カンマ区切り |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080` | カンマ区切り |
| `DJANGO_DB_PATH` | `db.sqlite3` (compose では `/data/db.sqlite3`) | SQLite のパス |

## 開発

```bash
docker compose run --rm api ruff check .
docker compose run --rm api ruff format --check .
docker compose run --rm api python manage.py test
docker compose run --rm api pip-audit -r requirements.txt
```

## Requirements
1. Use with **cshimegi/lucky-draw-gui**

## Installation from scratch (Docker なし)

```bash
git clone https://github.com/yuu-eguci/lucky-draw-api.git
cd lucky-draw-api
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
DJANGO_DEBUG=1 python manage.py migrate
DJANGO_DEBUG=1 python manage.py runserver 0.0.0.0:8080
```

## Access to Django WEB
After dev django server is ready, you can access API page from browser.

`http://localhost:8080/api/v1`
