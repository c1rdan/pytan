
Get All Sensors
==========================================================================================

Get all sensor objects


Step 1 - Authenticate to the SOAP API via /auth
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* URL: https://172.16.31.128:443/auth
* HTTP Method: GET
* Elapsed Time: 0:00:00.013533
* `Step 1 Request Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_1_request.txt>`_
* `Step 1 Response Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_1_response.txt>`_

* Request Headers:

.. code-block:: json
    :linenos:

    
    {
      "Accept": "*/*", 
      "Accept-Encoding": "gzip, deflate", 
      "Connection": "keep-alive", 
      "User-Agent": "python-requests/2.7.0 CPython/2.7.10 Darwin/14.5.0", 
      "password": "VGFuaXVtMjAxNSE=", 
      "username": "QWRtaW5pc3RyYXRvcg=="
    }

* Response Headers:

.. code-block:: json
    :linenos:

    
    {
      "connection": "Keep-Alive", 
      "content-encoding": "gzip", 
      "content-length": "110", 
      "content-type": "text/plain; charset=us-ascii", 
      "date": "Sat, 05 Sep 2015 05:36:24 GMT", 
      "keep-alive": "timeout=5, max=100", 
      "server": "Apache", 
      "strict-transport-security": "max-age=15768000", 
      "vary": "Accept-Encoding", 
      "x-frame-options": "SAMEORIGIN"
    }


Step 2 - Get the server version via /info.json
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* URL: https://172.16.31.128:443/info.json
* HTTP Method: GET
* Elapsed Time: 0:00:00.001279
* `Step 2 Request Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_2_request.txt>`_
* `Step 2 Response Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_2_response.txt>`_

* Request Headers:

.. code-block:: json
    :linenos:

    
    {
      "Accept": "*/*", 
      "Accept-Encoding": "gzip, deflate", 
      "Connection": "keep-alive", 
      "User-Agent": "python-requests/2.7.0 CPython/2.7.10 Darwin/14.5.0", 
      "session": "25-1640-f8084e14b83b6f04db4f745bddb707eff844b93317ded6ada8aee34e8b4716bac7583a7d995872d6602e0ae4ffb951399cd90229354d6831b574ff7a07755861"
    }

* Response Headers:

.. code-block:: json
    :linenos:

    
    {
      "connection": "Keep-Alive", 
      "content-length": "207", 
      "content-type": "text/html; charset=iso-8859-1", 
      "date": "Sat, 05 Sep 2015 05:36:24 GMT", 
      "keep-alive": "timeout=5, max=99", 
      "server": "Apache", 
      "x-frame-options": "SAMEORIGIN"
    }


Step 3 - Get the server version via /info.json
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* URL: https://172.16.31.128:444/info.json
* HTTP Method: POST
* Elapsed Time: 0:00:00.005786
* `Step 3 Request Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_3_request.txt>`_
* `Step 3 Response Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_3_response.json>`_

* Request Headers:

.. code-block:: json
    :linenos:

    
    {
      "Accept": "*/*", 
      "Accept-Encoding": "gzip, deflate", 
      "Connection": "keep-alive", 
      "Content-Length": "0", 
      "User-Agent": "python-requests/2.7.0 CPython/2.7.10 Darwin/14.5.0", 
      "session": "25-1640-f8084e14b83b6f04db4f745bddb707eff844b93317ded6ada8aee34e8b4716bac7583a7d995872d6602e0ae4ffb951399cd90229354d6831b574ff7a07755861"
    }

* Response Headers:

.. code-block:: json
    :linenos:

    
    {
      "content-length": "11014", 
      "content-type": "application/json"
    }


Step 4 - Issue a GetObject to find an object
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

* URL: https://172.16.31.128:443/soap
* HTTP Method: POST
* Elapsed Time: 0:00:00.116335
* `Step 4 Request Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_4_request.xml>`_
* `Step 4 Response Body <../../_static/soap_outputs/6.2.314.3321/get_all_sensors_step_4_response.xml>`_

* Request Headers:

.. code-block:: json
    :linenos:

    
    {
      "Accept": "*/*", 
      "Accept-Encoding": "gzip", 
      "Connection": "keep-alive", 
      "Content-Length": "470", 
      "Content-Type": "text/xml; charset=utf-8", 
      "User-Agent": "python-requests/2.7.0 CPython/2.7.10 Darwin/14.5.0", 
      "session": "25-1640-f8084e14b83b6f04db4f745bddb707eff844b93317ded6ada8aee34e8b4716bac7583a7d995872d6602e0ae4ffb951399cd90229354d6831b574ff7a07755861"
    }

* Response Headers:

.. code-block:: json
    :linenos:

    
    {
      "connection": "Keep-Alive", 
      "content-encoding": "gzip", 
      "content-length": "635511", 
      "content-type": "text/xml;charset=UTF-8", 
      "date": "Sat, 05 Sep 2015 05:36:24 GMT", 
      "keep-alive": "timeout=5, max=98", 
      "server": "Apache", 
      "strict-transport-security": "max-age=15768000", 
      "x-frame-options": "SAMEORIGIN"
    }


.. rubric:: Footnotes

.. [#] this file automatically created by BUILD/build_api_examples.py
