from .celery import app

@app.task(name='bill_yesterday_count',
          bind=True, autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 2, 'countdown': 0.5})
def bill_yesterday_count(self):
    print('hello', '$'*50)