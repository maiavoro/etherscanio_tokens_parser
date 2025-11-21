# Etherscan Parser

Cкрипт, который забирает парсит токенов со страницы Etherscan Tokens и сохраняет результат в **JSON**, отсортированный по цене (USD) по убыванию.

## Установка 

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Запуск

Онлайн (берёт данные с Etherscan):
```bash
python parse_crypto.py --limit 30 --out tokens.json
```

Локальный HTML:
```bash
python parse_crypto.py --source ./tokens.html --limit 100 --out tokens_local.json
```

URL явно:
```bash
python parse_crypto.py --source https://etherscan.io/tokens --limit 50 --out out.json
```

## Что попадает в JSON
```json
[
  {"token": "Wrapped BTC (WBTC)", "price_usd": 86333.0, "url": "https://etherscan.io/token/0x..."},
  ...
]
```