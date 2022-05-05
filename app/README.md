# Simple ML Model Server

## Relavent Files 
```
├── requirements.txt                   <- Python packages for s2i application
├── 0_start_here.ipynb                 <- Instructional notebook
├── 1_run_flask.ipynb                  <- Notebook for running flask locally to test
├── 2_test_flask.ipynb                 <- Notebook for testing flask requests
├── 3_packaging_application.ipynb      <- Notebook for building and depploying the model server
├── .gitignore              <- standard python gitignore
├── .s2i                    <- hidden folder for advanced s2i configuration
│   └── environment         <- s2i environment settings
├── gunicorn_config.py      <- configuration for gunicorn when run in OpenShift
├── prediction.py           <- the predict function called from Flask
└── wsgi.py                 <- Basic Flask application with Prometheus metrics instrumentation.
```

#### Build and Deploy the Model Server from the Openshift Command Line

#### Log in to OpenShift
```shell
oc login --token=sha256~XYZ --server=https://api.my-cluster:6443
```
#### Create a new OpenShift Project
Create a new project namespace.
```shell
oc new-project my-model-server
```

#### Create the OpenShift Application
```shell
oc new-app --image-stream=python:3.8-ubi8 --context-dir=/app --env=GUNICORN_CMD_ARGS="--bind=0.0.0.0:8080" https://github.com/redhat-na-ssa/fraud-detection-workshop.git
```
Observe the new application workload as it is deployed.  This should included a Deployment, BuildConfig, and Service.  You can navigate to your newly created project and view the topology from the Openshift Web Console.

#### Create a Route
To use the service endpoint externally, expose a route to the new endpoint.  
```shell
oc expose svc rhods-fraud-detection-workshop
```

#### Testing the Model Server 

The health of the application's service endpoint can be tested using cURL from the Openshift terminal.
```
HOST=$(oc get route fraud-detection-workshop --template='{{ .spec.host }}')

curl ${HOST} 
```
Expected Output
```
{"status":"ok"}
```

Making a sample prediction.

```
curl -k -X POST -d '{"user_id": 1698, "amount": 7915, "merchant_id": 22.37, "trans_type": "contactless", "foreign": "False", "interarrival": 9609}'  -H 'Content-Type: application/json' ${HOST}/predictions
```

Expected Output
```
{"prediction":"legitimate"}
```





