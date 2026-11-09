
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import json
import secrets

HOST, PORT = "127.0.0.1", 8000
FLAG = "CTF{requests_headers_cookies_json_redirects}"

SESSIONS = set()
TICKETS = set()


class Handler(BaseHTTPRequestHandler):

    def reply(self, status, data, headers=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))

        for name, value in (headers or {}).items():
            self.send_header(name, value)

        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 10_000:
                return None
            return self.rfile.read(size)
        except (ValueError, OSError):
            return None

    def session_ok(self):
        cookie = self.headers.get("Cookie", "")
        parts = [part.strip() for part in cookie.split(";")]

        return any(
            part.startswith("ctf_session=")
            and part.split("=", 1)[1] in SESSIONS
            for part in parts
        )

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Этап 1: начальная страница
        if path == "/":
            return self.reply(200, {
                "message": "Добро пожаловать в HTTP CTF!",
                "next": "GET /api/hello?name=student",
                "hint": "Используйте requests.Session()"
            })

        # Этап 2: один GET-параметр
        if path == "/api/hello":
            if query.get("name") != ["student"]:
                return self.reply(400, {
                    "error": "Нужен параметр name=student"
                })

            return self.reply(200, {
                "message": "Отлично!",
                "next": "GET /api/search?category=ctf&limit=3"
            })

        # Этап 3: несколько GET-параметров
        if path == "/api/search":
            if (
                query.get("category") != ["ctf"]
                or query.get("limit") != ["3"]
            ):
                return self.reply(400, {
                    "error": "Нужны category=ctf и limit=3"
                })

            return self.reply(200, {
                "results": ["web", "crypto", "pwn"],
                "next": "GET /api/header",
                "hint": (
                    "Добавьте заголовок X-CTF-Client "
                    "со значением python-requests"
                )
            })

        # Этап 4: HTTP-заголовок
        if path == "/api/header":
            if self.headers.get("X-CTF-Client") != "python-requests":
                return self.reply(403, {
                    "error": "Неверный заголовок X-CTF-Client"
                })

            return self.reply(200, {
                "next": "POST /api/login",
                "content_type": "application/x-www-form-urlencoded",
                "fields": {
                    "username": "student",
                    "password": "ctf123"
                }
            })

        # Этап 6: проверка cookies
        if path == "/api/profile":
            if not self.session_ok():
                return self.reply(401, {
                    "error": "Нужна cookie из /api/login"
                })

            return self.reply(200, {
                "user": "student",
                "role": "player",
                "next": "POST /api/unlock",
                "content_type": "application/json",
                "body": {
                    "action": "unlock",
                    "code": 1337
                }
            })

        # Этап 8: редирект
        if path == "/api/jump":
            if not self.session_ok():
                return self.reply(401, {
                    "error": "Сначала авторизуйтесь"
                })

            ticket = secrets.token_hex(6)
            TICKETS.add(ticket)

            self.send_response(302)
            self.send_header(
                "Location",
                f"/api/flag?ticket={ticket}"
            )
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # Этап 9: получение флага
        if path == "/api/flag":
            if not self.session_ok():
                return self.reply(401, {
                    "error": "Нужна cookie сессии"
                })

            ticket = query.get("ticket", [""])[0]

            if ticket not in TICKETS:
                return self.reply(403, {
                    "error": "Нужен ticket из редиректа"
                })

            TICKETS.remove(ticket)

            return self.reply(200, {
                "flag": FLAG,
                "message": "Задание выполнено!"
            })

        return self.reply(404, {
            "error": "Такого URL нет",
            "hint": "Начните с GET /"
        })

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()

        if body is None:
            return self.reply(400, {
                "error": "Некорректное тело запроса"
            })

        # Этап 5: POST с данными формы
        if path == "/api/login":
            content_type = (
                self.headers.get("Content-Type", "")
                .split(";")[0]
                .strip()
                .lower()
            )

            if content_type != "application/x-www-form-urlencoded":
                return self.reply(415, {
                    "error": "Используйте data=, а не json="
                })

            fields = parse_qs(
                body.decode("utf-8", errors="replace")
            )

            if (
                fields.get("username") != ["student"]
                or fields.get("password") != ["ctf123"]
            ):
                return self.reply(403, {
                    "error": "Неверные данные"
                })

            token = secrets.token_hex(16)
            SESSIONS.add(token)

            return self.reply(
                200,
                {
                    "message": "Вы вошли",
                    "next": "GET /api/profile"
                },
                {
                    "Set-Cookie": (
                        f"ctf_session={token}; "
                        "HttpOnly; Path=/; SameSite=Lax"
                    )
                }
            )

        # Этап 7: POST с JSON
        if path == "/api/unlock":
            if not self.session_ok():
                return self.reply(401, {
                    "error": "Сначала авторизуйтесь"
                })

            content_type = (
                self.headers.get("Content-Type", "")
                .split(";")[0]
                .strip()
                .lower()
            )

            if content_type != "application/json":
                return self.reply(415, {
                    "error": "Отправьте JSON через json="
                })

            try:
                obj = json.loads(body)
            except (ValueError, UnicodeDecodeError):
                return self.reply(400, {
                    "error": "Некорректный JSON"
                })

            if obj != {"action": "unlock", "code": 1337}:
                return self.reply(400, {
                    "error": "Нужны action=unlock и code=1337"
                })

            return self.reply(200, {
                "next": "GET /api/jump",
                "hint": "Следующий запрос вернёт редирект 302"
            })

        return self.reply(404, {
            "error": "Неизвестный POST URL"
        })


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)

    print(f"CTF server: http://{HOST}:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
