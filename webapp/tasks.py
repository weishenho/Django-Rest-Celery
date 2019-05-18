from __future__ import absolute_import

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from django.apps import apps
import random
from django.conf import settings
from .models import Total_files
import glob
import os
import json
from rest_framework.parsers import JSONParser
from django.db import models, connection, migrations
from .views import create_model


logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(minute="*/10")))
def randomly_increment_total_docs():
    models = apps.all_models['webapp']
    models_with_total_docs = [ model for model in models.keys() if "_data" in model ]
    random_model = random.choice(models_with_total_docs)
    selected_model = models[random_model]
    obj = selected_model.objects.order_by('?').first()
    logger.info("before increment " + str(random_model)  +  " " + str(obj.id) + " " + str(obj.total_docs) )
    obj.total_docs +=  1
    obj.save()
    logger.info("after increment " + str(random_model)  +  " " + str(obj.id) + " " + str(obj.total_docs) )

@periodic_task(run_every=(crontab(minute="*/1")))
def calc_total_files():
    directory = settings.FILE_UPLOAD
    files = glob.glob(directory + "/*.json")
    num_files = len(files)
    new_total_files = Total_files(total_files=num_files)
    new_total_files.save()

@periodic_task(run_every=(crontab(minute="*/30")))
def write_objs_to_files():
    directory = settings.FILE_UPLOAD
    files = glob.glob(directory + "/*.json")
    for f in files:
        model_name =  os.path.basename(os.path.splitext(f)[0])
        model = apps.get_model(app_label="webapp", model_name=model_name)
        data = list(model.objects.values())

        save_to = os.path.join(settings.FILE_UPLOAD, model_name + '.json')
        with open(save_to, 'w') as f:
            json.dump(data, f, indent=2)

# @task(name="model_upload_task")
# def model_upload_task(data, uploaded_file_name):
#     fields = {}
#     for key in data[0].keys():
#         if key == "id":
#             continue

#         datatype = type(data[0][key])
#         if datatype is int:
#             fields[key] = models.IntegerField()
#         else: 
#             fields[key] = models.CharField(max_length=255)

#     model_name =  os.path.splitext(uploaded_file_name)[0]
#     created_model = create_model(model_name, fields, 'webapp')

#     with connection.schema_editor() as schema_editor:
#         schema_editor.create_model(created_model)

#     for record in data:
#         created_obj = created_model(**record)
#         created_obj.save()