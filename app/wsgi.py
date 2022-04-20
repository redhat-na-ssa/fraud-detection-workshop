import json
from pydoc import pager
from flask import Flask, jsonify, request
from prediction import predict
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import start_http_server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import logging
import time

application = Flask(__name__)

#
# Define the Prometheus metrics.
#
c = Counter('model_server_requests_count', 'Requests Counter')
legit = Counter('model_server_legit_count', 'Legitimate Counter')
fraud = Counter('model_server_fraud_count', 'Fraud Counter')
elapsedTime = Gauge('model_server_elapsed', 'Elapsed Time Gauge')

logging.basicConfig(level=logging.INFO)

@application.route('/')
@application.route('/status')
def status():
    return jsonify({'status': 'ok'})


@application.route('/predictions', methods=['POST'])
def create_prediction():
    t0 = time.time()
    c.inc()
    data = request.data or '{}'
    body = json.loads(data)
    p = predict(body)
    
    #
    # Increment the prediction counts.
    #
    if p["prediction"] == "legitimate":
            legit.inc()
    if p["prediction"] == "fraud":
            fraud.inc()

    logging.debug(f'Prediction: {p["prediction"]}')
    
    r = jsonify(p)
    elapsedTime.set(time.time() - t0)
    return r

#
# Add prometheus wsgi middleware to route /metrics requests
#
application.wsgi_app = DispatcherMiddleware(application.wsgi_app, {
    '/metrics': make_wsgi_app()
})
