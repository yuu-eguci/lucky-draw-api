RESTful API for Lucky Draw
===

抽選アプリ [lucky-draw-gui](https://github.com/cshimegi/lucky-draw-gui) の参加者を登録・取得・更新・削除する API。

- Docker: 対応!
- Python: 3.14!
- Linter: Ruff!
- Test: Django test runner (unittest) + DRF APIClient!
- Django: 5.2.18 (LTS)!
- Django REST framework: 3.18.3!

## パッと実行してみたい

```bash
docker compose up --build
# 別のターミナルで
curl -X POST http://localhost:8080/api/v1/attendee/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "taro", "email": "taro@example.com", "phone": "09012345"}'
curl http://localhost:8080/api/v1/attendee/
```

- 起動時に DB を準備して、開発サーバを `localhost:8080` で立ち上げる。
- POST の例で参加者を1人登録し、続く GET で一覧を取得する。
- データは Docker volume の SQLite に保存する。コンテナを作り直しても残る。 `docker compose down --volumes` で消える。
- ブラウザで `http://localhost:8080/api/v1/` を開くと、DRF の画面から API を試せる。
- 開発用・認証なし。自分の PC からだけアクセスできる設定なので、インターネットには公開しない。
- 同じ登録例をもう一度送ると、メールアドレスと電話番号の重複で 400 が返る。

## ダミーの参加者を入れたい

```bash
docker compose run --rm --build api python manage.py seed_attendees --count 30
```

- `seed0001@example.com` のようなダミーの参加者を `--count` 人 (既定 10 人、最大 9999 人) 登録します。
- もう一度実行しても、登録済みのダミーは追加されません。
- 起動中のサービスと同じ Docker volume の DB に登録されます。

## 参加者データを退避・復元したい

```bash
docker compose run --rm -T api python manage.py dumpdata attendee --indent 2 > attendees.json
docker compose run --rm -T api python manage.py loaddata --format json - < attendees.json
```

- 復元は同じ id の参加者を上書きします。
- `attendees.json` には参加者の個人情報が入るので、取り扱いに注意してください。

## API

| メソッド | パス | 内容 |
|---|---|---|
| GET | `/api/v1/attendee/` | 一覧 |
| POST | `/api/v1/attendee/` | 登録 |
| GET | `/api/v1/attendee/{id}/` | 1件取得 |
| PUT / PATCH | `/api/v1/attendee/{id}/` | 更新 |
| DELETE | `/api/v1/attendee/{id}/` | 削除 |

```bash
# 登録時に返った id を使う。ここでは 1 とする。
curl http://localhost:8080/api/v1/attendee/1/
curl -X PUT http://localhost:8080/api/v1/attendee/1/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "taro", "email": "taro@example.com", "phone": "0901234567"}'
curl -X PATCH http://localhost:8080/api/v1/attendee/1/ \
  -H 'Content-Type: application/json' -d '{"name": "jiro"}'
curl -X DELETE http://localhost:8080/api/v1/attendee/1/
```

- 末尾の `/` は省略しても同じように動く。返る URL は `/` 付き。
- `curl http://localhost:8080/api/v1/` でエンドポイント一覧 (JSON) を取得できる。
- 入力エラーは 400。 `{"phone": ["..."]}` のように項目ごとの JSON が返る。
- `name`: 1-64 文字。日本語も使える。
- `email`: メールアドレス。重複不可。
- `phone`: 8-10 文字の英数字・`-`・`_`。重複不可。先頭の 0 を残すため、文字列で送る。
- 同じ API は昔からの `/admin/attendee/` でも呼べる。

## 設定 (環境変数)

| 変数 | 既定値 | 内容 |
|---|---|---|
| `DJANGO_DEBUG` | `0` (compose では `1`) | `1` で開発用 DEBUG を有効化。 `0` では DRF 画面の CSS は配信されません (JSON API は動きます) |
| `DJANGO_SECRET_KEY` | DEBUG 時だけ開発用の値 | DEBUG でないときは必須 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | カンマ区切り |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080` | カンマ区切り |
| `DJANGO_DB_PATH` | `db.sqlite3` (compose では `/data/db.sqlite3`) | SQLite のパス |

## 開発

```bash
docker compose run --rm --build api ruff check .
docker compose run --rm --build api ruff format --check .
docker compose run --rm --build api python manage.py makemigrations --check --dry-run
docker compose run --rm --build api python manage.py test
docker compose run --rm --build api pip-audit -r requirements.txt
```

- コードはイメージに入るので、 `--build` で最新のコードからイメージを作り直してから実行します。

起動中のサービスへ実際に HTTP を送って、登録から削除までを確認できます。

```bash
docker compose up --build --detach --wait
sh scripts/smoke.sh
```

- `scripts/smoke.sh` は毎回ちがう参加者を1人登録し、最後に削除します。
- 確認先は `SMOKE_BASE_URL` (既定 `http://localhost:8080`) で変えられます。

## Docker なしで起動する

```bash
git clone https://github.com/yuu-eguci/lucky-draw-api.git
cd lucky-draw-api
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
DJANGO_DEBUG=1 python manage.py migrate
DJANGO_DEBUG=1 python manage.py runserver 127.0.0.1:8080
```

- Windows の PowerShell では、先に `$env:DJANGO_DEBUG = "1"` を実行してから `python manage.py ...` を実行します。
- テストは `DJANGO_DEBUG=1 python manage.py test` で実行します。

起動後は `http://localhost:8080/api/v1/` を開けば OK。
Docker なしの場合、データはプロジェクト内の `db.sqlite3` に保存する。
