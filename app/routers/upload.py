from fastapi import APIRouter
from celery.result import AsyncResult
from app.tasks import index_document, ask_question
from redis import Redis
import json

r = Redis(host="localhost", port=6379, decode_responses=True)
router = APIRouter(prefix="/knowledge-bases/{kb_id}", tags=["upload"])
@router.get("/task/{task_id}")
async def get_task_status(task_id:str):
    cache_key = f"task_result:{task_id}"
    redis_client = r.get(cache_key)
    if redis_client is not None:
        result = json.loads(redis_client)
        return {"status": "done", "result": result}
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        result = task.result
        r.set(cache_key,json.dumps(result),ex=3600)
        return {"status": "done", "result": result}
    elif task.state =="FAILURE":
        return {"status": "failed", "error": str(task.info)}
    return {"status":task.state,"meta":task.info}

@router.get("/tasks")
async def get_all_tasks():
    task_ids = r.smembers("active_tasks")
    results = []
    for tid in task_ids:
        task = AsyncResult(tid)
        results.append({"task_id": tid, "status": task.state, "meta": task.info or {}})
    return results