Trac Search
===========

Bring the modernity of Elastic Search to the classical Trac.

Trac is a nice tool, but it search engine is confusing.

![Screenshot](screenshot.png)

Install it
----------

Create a nice virtualenv.

    pip install -r requirements.txt
    python setup.py install

Try it
------

Launch a local elastic.

Configure

    cp tracsearch.ini.sample tracsearch.ini
    vim tracsearch.ini

Index some tickets

    index_ticket.py

Launch the web application

    python -m tracsearch.web

Deploy it
---------

For now, there is no automatic indexation.

### Virtualenv and supervisord

Use supervisord to launch the web application.

Use the source folder as virtualenv folder.

Edit _/etc/supervisor/conf.d/tracsearch.conf_

    [program:tracsearch]
    user=tracsearch
    command=/opt/tracsearch/bin/python web.py
    directory=/opt/tracsearch
    environment=PATH="/opt/tracsearch/bin"

### Sentry

You can use [Sentry](http://www.getsentry.com/) to watch Tracsearch's errors.

Grab your sentry dsn and add it to tracsearch.ini

    [sentry]
    dsn=http://public_key:secret_key@example.com/1

You can use Tracseerch without a _sentry_ section in the conf file.


Todo
----

 - √ Index ticket and comment
 - √ Index wiki
 - √ Web UI
 - √ Time line
 - √ Sentry integration
 - _ Multiple Trac
 - _ Trac module to live index
 - _ Redmine variant
 - _ Blood hound integration

Licence
-------

BSD © Mathieu Lecarme 2013
