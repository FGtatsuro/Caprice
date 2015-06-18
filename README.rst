Caprice
===========

JSON-resource manager

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