#!/usr/bin/python
from flaskapp import app
app.run(debug = False, host='0.0.0.0',port=5555,threaded=True)
