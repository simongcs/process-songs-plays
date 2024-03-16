from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery
