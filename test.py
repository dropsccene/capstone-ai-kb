curl -N -X POST http://localhost:8000/knowledge-bases/3/ask-stream \
    -H "Content-Type: application/json" \
    -d '{"question":"向量数据库是什么"}'