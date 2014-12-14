# -*- coding: utf-8 -*-
from celery import Celery
from celery.task import periodic_task
from datetime import timedelta
from settings import Config
from mongoengine import connect
celery = Celery('tasks',broker='redis://localhost:6379/2')
from pyquery import PyQuery as pq
from public.models import Apartment

from flask_mail import Message
from extensions import mail

URL = 'http://berlin.en.craigslist.de/search/apa'


db = Config.MONGODB_SETTINGS['DB']
connect(db)

@periodic_task(run_every=timedelta(hours=1))
def get_apartments():
    page = pq(URL)
    page.make_links_absolute(base_url=URL)
    for row in page('.row'):
        apartment = Apartment()
        apartment.url =  pq(row)('.pl a').attr('href')
        apartment.title = pq(row)('.pl a').text()
        apartment.price = int(pq(row)('.price').text()[1:])
        if len(Apartment.objects.filter(url=apartment.url)) == 0:
            apartment.save()


@periodic_task(run_every=timedelta(hours=6))
def send_report():
    top_five = Apartment.objects.order_by('price').limit(5)
    email = ''
    for apartment in top_five:
        email += '\n -------- \n %s - %s %s' % (apartment.title, apartment.price, apartment.url)

    msg = Message(
            subject='Apartment Report from your Minion !',
            sender = 'user@gmail.com',
            recipients=['youremail@gmail.com'],
            body=email
            )
    mail.send(msg)

