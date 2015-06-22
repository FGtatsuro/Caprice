Caprice
===========

JSON-resource manager

API
---

EndPoint: /api

- GET /schemas
- POST /schemas
- GET /schemas/<id>
- DELETE /schemas/<id>

- GET /resources
- POST /resources
- GET /resources/<id>
- PUT /resources/<id>
- DELETE /resources/<id>

- GET /locks
- POST /locks
- GET /locks/<id>
- DELETE /locks/<id>

Run the application on local
----------------------------

.. code:: bash

    $ pip install -r requirements.txt
    $ uwsgi uwsgi.ini

Run the application on Heroku
-----------------------------

.. code:: bash

    $ git init && git add . && git commit -m 'init'
    $ heroku create $(yourappname)
    $ git push heroku master
