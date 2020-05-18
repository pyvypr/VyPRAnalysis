Getting Started
=================================================

To get started with the VyPR Analysis Library, follow the instructions [here](http://cern.ch/vypr/use-vypr.html)
and then begin with the very simple script:

.. code-block:: python

   import VyPRAnalysis as va
   va.set_server("http://localhost:8080/")

This script will establish a connection to a locally-running VyPR server.  From here, the whole analysis library is
accessible via the `va` variable.

Your next step is to query your verdict server for some objects, so have a look at :doc:`querying`.