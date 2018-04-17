# bugzilla-loadtests

## Description
This repo contains the following scripts:
* test_bugzilla.py - pytest script for generating real bugs with content and of a size that can be useful for loadtesting
* loadtest.py - molotov script for generatring traffic using the real bugs created with test_bugzilla.py 

The loadtests in this repo will create traffic against the real bugs generated via the following web views:
* show_bug
* showdependencytree 
* buglist

NOTE:
* these tests do not loadtest every web API of the bugzilla service.


## Warning
* These tests are intended for checking the performance and scalability of your own
  bugzilla instance
* DO NOT RUN THESE TESTS AGAINST ANY SERVER YOU DON'T OWN 
* YOU HAVE BEEN WARNED

## Setup
Run test_bugzilla.py to generate all the bugs you'd like to use for testing.

NOTE:
The bug size and content can be easily adapted. Some characteristics that can be changed are:
* Bug title size
* Number of comments
* "Linkify" (or not) each comment
* Fixed comment size
* Randomize comment size across a size range: (min: max)
* Comment content (see: /data dir)


```
pytest ./test_bugzilla.py
```

## Loadtest

### Summary
Loadtests use the molotov framework.  see the /scripts directory for an example of how
to build and execute the test Docker container
* env - set all our env vars here (though safer to put your BUGZILLA_API_KEY in your bash profile)
* build - will generate your Docker image
** note: you must have previously completed Setup as the Docker build will grab you .cache dir and 
   load it into your Docker image
* run - will source your env file and execute the test

### Execution 
After you build your Docker container, you can run it (see: /scripts/run file)

To choose which loadtest you wish to run, open env file and flag the WEIGHT from 0 to 1 
to activate the test. For more discrete results, only flag one test at a time.
TEST_DURATION - is in seconds
TEST_PROCESSES, TEST_CONNECTIONS - these setting allow you to drive traffice from more than one agent from your
single laptop/desktop host.  See molotov docs for more info.  Please note, that you will eventually be limited
by the bandwidth of your own host.  

For unlimited traffic generation, your Docker container may be used with a tool like ardere, which will
spin up an attack cluster for you on AWS.  A sample ardere.json file can be found in this repo.
