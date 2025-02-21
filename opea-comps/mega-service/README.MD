```bash
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-coder:1.15b-instruct",
    "messages": "Write a python function that calculates the fibonacci sequence"
  }' \
  -o response.json

```

```bash
curl -X POST http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": "Explain quantum physics in simple terms.",
    "model": "deepseek-coder:1.15b-instruct",
    "max_tokens": 200,
    "temperature": 0.8
  }'
```

