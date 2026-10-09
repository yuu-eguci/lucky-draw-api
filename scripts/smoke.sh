#!/bin/sh
# 起動中の API へ実際に HTTP を送り、登録から削除までの流れを確認します。
# 使い方: sh scripts/smoke.sh  (確認先は SMOKE_BASE_URL で変更できます)
set -eu

BASE_URL="${SMOKE_BASE_URL:-http://localhost:8080}"
API="$BASE_URL/api/v1/attendee"
SUFFIX="$(date +%s)$$"
EMAIL="smoke-$SUFFIX@example.com"
PHONE="$(printf '%s' "$SUFFIX" | tail -c 10)"
BODY_FILE="$(mktemp)"
ID=""

cleanup() {
    # 途中で失敗しても、登録した参加者を残さないように削除します
    if [ -n "$ID" ]; then
        curl -sS -o /dev/null -X DELETE "$API/$ID/" || true
    fi
    rm -f "$BODY_FILE"
}
trap cleanup EXIT

fail() {
    echo "NG: $1" >&2
    cat "$BODY_FILE" >&2
    echo >&2
    exit 1
}

# request <期待するステータス> <説明> <curl の引数...>
request() {
    expected="$1"
    label="$2"
    shift 2
    status="$(curl -sS -o "$BODY_FILE" -w '%{http_code}' "$@")" || fail "$label: 接続できません"
    [ "$status" = "$expected" ] || fail "$label: $expected のはずが $status"
    echo "OK: $label ($status)"
}

json() {
    request "$1" "$2" -H 'Content-Type: application/json' -X "$3" -d "$4" "$5"
}

request 200 "API root" "$BASE_URL/api/v1/"
grep -q '"attendee"' "$BODY_FILE" || fail "API root に attendee がありません"

json 201 "登録" POST "{\"name\": \"smoke\", \"email\": \"$EMAIL\", \"phone\": \"$PHONE\"}" "$API/"
ID="$(sed -n 's/.*"id":\([0-9][0-9]*\).*/\1/p' "$BODY_FILE")"
[ -n "$ID" ] || fail "登録結果に id がありません"

request 200 "1件取得" "$API/$ID/"
grep -q "\"email\":\"$EMAIL\"" "$BODY_FILE" || fail "取得結果の email が違います"

json 400 "重複登録" POST "{\"name\": \"smoke\", \"email\": \"$EMAIL\", \"phone\": \"$PHONE\"}" "$API/"
grep -q '"email"' "$BODY_FILE" || fail "重複エラーに email がありません"

json 400 "短すぎる phone" PATCH '{"phone": "1234567"}' "$API/$ID/"
json 200 "末尾 / なしの PATCH" PATCH '{"name": "smoke2"}' "$API/$ID"
grep -q '"name":"smoke2"' "$BODY_FILE" || fail "PATCH が反映されていません"

curl -sS -o /dev/null -D "$BODY_FILE" -H 'Origin: http://localhost:3000' "$API/" || fail "CORS: 接続できません"
ALLOW_ORIGIN="$(tr -d '\r' < "$BODY_FILE" | sed -n 's/^[Aa]ccess-[Cc]ontrol-[Aa]llow-[Oo]rigin: //p')"
[ "$ALLOW_ORIGIN" = "http://localhost:3000" ] || fail "CORS ヘッダがありません"
echo "OK: CORS (http://localhost:3000)"

curl -sS -o /dev/null -D "$BODY_FILE" -X OPTIONS -H 'Origin: http://localhost:3000' \
    -H 'Access-Control-Request-Method: DELETE' -H 'Access-Control-Request-Headers: content-type' \
    "$API/$ID/" || fail "CORS preflight: 接続できません"
tr -d '\r' < "$BODY_FILE" | grep -i '^access-control-allow-methods:.*DELETE' >/dev/null || fail "CORS preflight で DELETE が許可されていません"
echo "OK: CORS preflight (DELETE)"

request 204 "削除" -X DELETE "$API/$ID/"
DELETED_ID="$ID"
ID=""
request 404 "削除後の取得" "$API/$DELETED_ID/"

echo "smoke test: すべて OK"
