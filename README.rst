Twitter Analysis
===============

Twitter's API is annoying to work with, and has lots of limitations —
luckily their frontend (JavaScript) has it's own API, which Kennethreitz reverse–engineered.
No API rate limits. No restrictions. Extremely fast.

You can use this library to get the text of any user's Tweets and use the results for analysis.

Usage
=====

.. code-block:: pycon

    >>> from twitter_analysis import get_tweets

    >>> for tweet in get_tweets('kennethreitz', tweets=100):
    >>>     print(tweet)
    P.S. your API is a user interface
    s3monkey just hit 100 github stars! Thanks, y’all!
    I’m not sure what this /dev/fd/5 business is, but it’s driving me up the wall.
    …

It appears you can ask for up to 450 tweets reliably (25 html pages).

Installation
============

.. code-block:: shell

    $ pipenv install twitter-analysis

Only Python 3.6+ is supported


LICENSE
=======

MIT
