import json
from pydoc import pager
from flask import Flask, jsonify, request
from prediction import predict
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import logging
import time

application = Flask(__name__)

#
# Define the Prometheus metrics.
#
c = Counter('model_server_requests', 'Requests')
legit = Counter('model_server_legit_predictions', 'Legitimate Transactions')
fraud = Counter('model_server_fraud_predictions', 'Fraudulent Transactions')
# elapsedTime = Gauge('model_server_response_seconds', 'Response Time Gauge')
latency = Histogram('model_server_request_latency_seconds', 'Prediction processing time', buckets=[0.00525, 0.0055, 0.006, 0.00625, 0.0065, 0.007, 0.008])

logging.basicConfig(level=logging.INFO)

@application.route('/')
@application.route('/status')
def status():
    logging.info(f'{Flask.response_class()}')
    return jsonify({'status': 'ok'})

@latency.time()
@application.route('/predictions', methods=['POST'])
def create_prediction():
    #t0 = time.time()
    with latency.time():
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
        # elapsedTime.set(time.time() - t0)
        # latency.observe(time.time() - t0)
        return r

@application.errorhandler(404) 
def invalid_route(e): 
    logging.info(f'errorCode : 404, message : Route not found')
    return jsonify({'errorCode' : 404, 'message' : 'Route not found'})

#
# Add prometheus wsgi middleware to route /metrics requests
#
application.wsgi_app = DispatcherMiddleware(application.wsgi_app, {
    '/metrics': make_wsgi_app()
})
