Trac Search
===========

Bring the modernity of Elastic Search to the classical Trac.

Trac is a nice tool, but it search engine is confusing.

Install it
----------

Create a nice virtualenv.

    pip install -r requirements.txt

Try it
------

Launch a local elastic.

Export your trac URL

    export TRAC_URL=https://bob:toto@my.wonderful.trac/

Try the scripts

    ./index_wiki.py
    ./index_ticket.py

Install [head](http://mobz.github.com/elasticsearch-head/) in your elastic and watch your datas.

Todo
----

 * √ Index wiki, tiket and comment
 * _ Web UI
 * _ Multiple Trac
 * _ Trac module to live index
 * _ Redmine variant

Licence
-------

BSD © Mathieu Lecarme 2013
