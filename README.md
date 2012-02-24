pysatisfaction
==============

The is a start at a wrapper around GetSatisfaction's JSON API.  It was initially based on [python-satisfaction](https://github.com/gma/python-satisfaction) but as that module uses the XML API it quickly diverged.  

Improvements to be made:
    * The classes representing particular objects in the JSON response feel unnecessary and excessive.  They are a design carry over from python-satisfaction.
    * At the moment, this library supports the specific operations I needed at the time, it obviously should support all possible queries on the API
    * Paging of results currently isn't supported, but is pretty easy to implement, I just didn't need it.  Look for it soon

More to come.
