
import hashlib

# Секреты хранятся в виде SHA-256
HASHES = [
    "c79d7bc27b3d90b26e0b3ae8f10f7f6ad26d2db2e0ec4e62bbaf4d7116de4c35",
    "b96a4c5d1c9ee574e2e4ca3be9ab9e89dbb8e3e20a5d4c2f82aa3ef3513c9f47",
    "b5c2d4e7a8f190b6c3d5e7a9f102b4d6c8e0f2a4b6d8e1f3a5c7e9b0d2f4a6c8",
]

# Вычисляем реальные хеши для примера
SECRETS = ["cab", "bac", "ad"]
HASHES = [
    hashlib.sha256(s.encode()).hexdigest()
    for s in SECRETS
]

print("=== Secret Code ===")
print("Найдите три секретных строки по их SHA-256.\n")

print("1. Код длиной 3 из abc (символы могут повторяться)")
print("2. Перестановка трёх символов abc")
print("3. Сочетание двух символов из abcd (порядок алфавитный)\n")

for i, value in enumerate(HASHES, 1):
    print(f"SHA256_{i} = {value}")

answers = [
    input("Код 1: "),
    input("Код 2: "),
    input("Код 3: "),
]

if answers == SECRETS:
    print("FLAG: CTF{itertools_bruteforce_success}")
else:
    print("Неверные коды")
