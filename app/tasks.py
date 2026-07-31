from app.celery_app import celery_app
from redis import Redis
r = Redis(host="localhost", port=6379, decode_responses=True)


def do_chunk(file_path:str):
    pass

def do_search(question:str,kb_id:str):
    pass

@celery_app.task(bind=True)
def index_document(self,file_path:str,kb_id:str):
    r.sadd("active_tasks",self.request.id)
    self.update_state(state="PROCESSING",meta={"progress":30,"step":"chunking"})
    do_chunk(file_path)
    r.srem("active_tasks",self.request.id)
    return {"chunks":12,"kb_id":kb_id}


@celery_app.task(bind=True)
def ask_question(self,question:str,kb_id:str):
    r.sadd("active_tasks",self.request.id)
    self.update_state(state="PROCESSING",meta={"progress":50,"step":"retrieving"})
    do_search(question,kb_id)
    r.srem("active_tasks",self.request.id)
    return {"answer":"这是一个模拟回答","kb_id":kb_id}