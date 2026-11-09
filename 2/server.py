
import secrets
import socketserver

HOST = "127.0.0.1"
PORT = 19000

FLAG = "CTF{tcp_socket_bytes_and_parsing}"


class ChallengeHandler(socketserver.StreamRequestHandler):

    def send_line(self, message):
        """Отправить строку клиенту."""
        data = (message + "\n").encode("utf-8")
        self.wfile.write(data)
        self.wfile.flush()

    def handle(self):
        """Обработать подключение клиента."""
        self.connection.settimeout(15)

        # Случайный токен для каждого подключения
        token = secrets.token_hex(4)

        # Тип задания, входные данные, правильный ответ
        tasks = [
            ("PING", "PING", "PONG"),
            ("ECHO", "ctf_student", "ctf_student"),
            ("SUM", "17,25,8", "50"),
            ("REVERSE", "socket", "tekcos"),
            ("HEX", "68656c6c6f", "hello"),
            ("BASE64", "cHl0aG9u", "python"),
            ("CSV_MAX", "4,17,9,2", "17"),
            ("AUTH", token, f"AUTH {token}"),
        ]

        self.send_line(
            "WELCOME|Socket CTF: answer each task"
        )

        self.send_line(
            "INFO|Each answer must end with \\n"
        )

        for number, (kind, value, expected) in enumerate(tasks, 1):

            # Отправляем очередное задание
            self.send_line(f"TASK|{kind}|{value}")

            # Получаем одну строку от клиента
            raw = self.rfile.readline(4096)

            if not raw:
                return

            answer = raw.rstrip(b"\r\n").decode(
                "utf-8", errors="replace"
            )

            # Проверяем ответ
            if answer != expected:
                self.send_line(
                    f"ERROR|step={number}|wrong answer"
                )
                return

            self.send_line(f"OK|step={number}")

        # Все задания решены
        self.send_line(f"FLAG|{FLAG}")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server((HOST, PORT), ChallengeHandler) as server:
        print(f"Socket CTF: {HOST}:{PORT}")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
