# Simple real time analytics demo

## Objective 
To build a simple example of getting real time analytics (mean and standard deviation) of a simulated IoT sensor values (temperature/soil nitrogen content/moisture content etc). 

## Constraint
All the values generated since the sensor began operation are not stored in a database (we can choose to store them too, millions of entries too can be easily manageable by modern databases). Only the final analytics outputs are stored. Also the computation mechanism must accommodate for moving mean and standard deviation which should be the same as the true mean and std dev if we stored all the sensor values but there is no big machine available with enough RAM to accommodate millions of values generated by the sensor over time, hence the calculations must support an incremental approach. 

## Assumptions
The sensor operates 24/7 and it will work forever.

## Sample output
https://user-images.githubusercontent.com/23210132/179419147-538b8a66-1335-4874-b995-d1c0b9345753.mp4

Note: Just to show the possibilities of the UI, we've done a dummy run with the frontend to show if the values go below or above a threshold then how does the UI display those changes.

## What I aim to learn out of this pet project
Basics of Data Engineering using queue based solutions and an intuitive solution for incremental and real time analytics. Some math about the incremental mean and std dev. Also socketio.

## Methodology
We simulate an IoT sensor producing some value at fixed time intervals and our aim is to build a system which is real time in nature and provides us with the mean and standard deviation of the values generated till date. As per the constraints, we can't store all values generated so we must simulate streaming analytics with incremental updates. We use special formulas for mean and std dev calculations which support incoming new data (1 data point) and their output equals to the actual mean and std dev if all values are stored. The generation process is a simple random number generation written in python which acts as a Producer for the queue. The producer throws all the values on the queue (we use kafka as the event bus here). A consumer on the other end subscribes to this queue, listens to incoming messages, consumes them, does the calculation and stores them in a database (redis). These values are also then published to another queue which is meant for the updates to be sent to a simple websocket based Javascript backend server. A simple frontend displays the mean and standard deviation in an updating fashion with a socket.io connection.   

## Tech stack used
* Python for writing the producer and consumer codebase. 
* Javacript (node & express) for the socketio backend.
* React for the frontend.
* Kafka as an event bus (can easily use RabbitMQ, NATS, NATS streaming, redis pub/sub etc. instead)
* Redis as a database (coz why not! can use mongo too - preferrable some key value pair DB)
* Docker to containerize all individual deplyoments
* Helm as package manager for configuring deployment in the kubernetes cluster
* Kubernetes (k3s) for orchestration

# Architecture?
![Architecture_diagram drawio](https://user-images.githubusercontent.com/23210132/179452819-e2e889c4-03c5-41c1-9119-3a98e1691db6.png)



# Steps to follow along and replicate this project are as follows

All these modules can be run in a single machine. I run all this in a Google Cloud VM with 2 vCPU and 7.5 GB RAM with Ubuntu 18.04. 
Note: All these steps must be followed in the given order or we might see a lot of errors

## Prerequisites
* Docker - [Installation steps](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)


## Installing k3s
K3s is a lightweight version of the Kubernetes (K8s) API made to work on edge devices (IoT systems) such as a raspberry pi but it works perfectly well in a normal system.

Navigate to the following website: https://k3s.io/ and follow the steps given right on the first page to install it

If you see the following error: 

`
WARN[0000] Unable to read /etc/rancher/k3s/k3s.yaml, please start server with --write-kubeconfig-mode to modify kube config permissions 
error: error loading config file "/etc/rancher/k3s/k3s.yaml": open /etc/rancher/k3s/k3s.yaml: permission denied
`

Follow the steps given in [this answer](https://devops.stackexchange.com/questions/16043/error-error-loading-config-file-etc-rancher-k3s-k3s-yaml-open-etc-rancher) to set the permissions the right way


## Installing and configuring helm
Helm is a package manager for kubernetes - analogous to pip for python or npm for JS.

Just follow the steps mentioned here: https://helm.sh/docs/intro/install/

Note: The older helm client (v2) required to create a service account - tiller (remote component) to be able to create deployments in the kubernetes cluster, now its not needed.


## Running a local docker container registry
There could be times that we need to upload our docker images to some private registry due to propreitory work or secret assets. I generally use google cloud's registry but if you don't have a cloud provision or don't want to pay for a private space on docker hub, you can configure your own registry running in the same machine from where kubernetes can pull the docker images.

We can simply deploy our docker registry in our machine using the following command:

```
$ docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

To verify if the registry is up and running run

```
$ docker ps
```

The output should look something like this:

```
CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                       NAMES
2b3ee4a79eb5   registry:2   "/entrypoint.sh /etc???"   2 minutes ago   Up 2 minutes   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   registry
```

If you get any errors, google up the error - most of the docker errors are solved on Stack Overflow.
These steps are from https://docs.docker.com/registry/deploying/ where you might find extra steps to secure this registry.

## Deploying kafka in the k3s cluster
We use helm to install a kafka deployment in our cluster to save us the hassles of doing a custom kubernetes deployment (no good sources on the internet seems to have good documentation to deploy kafka in kubernetes using k8s manifests)

First add the bitnami repo where the official kafka chart resides
```
$ helm repo add bitnami https://charts.bitnami.com/bitnami
```
Then go ahead and install kafka in the cluster
```
$ helm install my-release bitnami/kafka
```

The output should look something like this:
```
NAME: my-release
LAST DEPLOYED: Sat Jul 16 16:55:52 2022
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: kafka
CHART VERSION: 18.0.3
APP VERSION: 3.2.0

** Please be patient while the chart is being deployed **

Kafka can be accessed by consumers via port 9092 on the following DNS name from within your cluster:

    my-release-kafka.default.svc.cluster.local

Each Kafka broker can be accessed by producers via port 9092 on the following DNS name(s) from within your cluster:

    my-release-kafka-0.my-release-kafka-headless.default.svc.cluster.local:9092

To create a pod that you can use as a Kafka client run the following commands:

    kubectl run my-release-kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.2.0-debian-11-r12 --namespace default --command -- sleep infinity
    kubectl exec --tty -i my-release-kafka-client --namespace default -- bash

    PRODUCER:
        kafka-console-producer.sh \
            
            --broker-list my-release-kafka-0.my-release-kafka-headless.default.svc.cluster.local:9092 \
            --topic test

    CONSUMER:
        kafka-console-consumer.sh \
            
            --bootstrap-server my-release-kafka.default.svc.cluster.local:9092 \
            --topic test \
            --from-beginning
```

After a few minutes we can check if the kafka deployments are ready to use
Run the following command to keep checking the status and the output should have the status "Running" for both zookeeper and kafka pods
```
$ kubectl get pods
NAME                     READY   STATUS    RESTARTS   AGE
my-release-zookeeper-0   1/1     Running   0          2m47s
my-release-kafka-0       1/1     Running   0          2m47s
```
The same instructions to deploy kafka can be found in the official bitnami helm charts documentations: https://bitnami.com/stack/kafka/helm

## Deploying redis in the k3s cluster
We deploy redis in a similar way we deployed kafka - using helm

The following command deploys a replicaset of redis in the cluster:

```
$ helm install my-redis bitnami/redis
```

The output should look something like this

```
NAME: my-redis
LAST DEPLOYED: Sat Jul 16 17:38:29 2022
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: redis
CHART VERSION: 17.0.1
APP VERSION: 7.0.3

** Please be patient while the chart is being deployed **

Redis&reg; can be accessed on the following DNS names from within your cluster:

    my-redis-master.default.svc.cluster.local for read/write operations (port 6379)
    my-redis-replicas.default.svc.cluster.local for read-only operations (port 6379)



To get your password run:

    export REDIS_PASSWORD=$(kubectl get secret --namespace default my-redis -o jsonpath="{.data.redis-password}" | base64 -d)

To connect to your Redis&reg; server:

1. Run a Redis&reg; pod that you can use as a client:

   kubectl run --namespace default redis-client --restart='Never'  --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:7.0.3-debian-11-r0 --command -- sleep infinity

   Use the following command to attach to the pod:

   kubectl exec --tty -i redis-client \
   --namespace default -- bash

2. Connect using the Redis&reg; CLI:
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h my-redis-master
   REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h my-redis-replicas

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace default svc/my-redis-master 6379:6379 &
    REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379
```

In a few seconds or minutes, we must see the redis deployments running along with the already deployed kafka:
```
kubectl get pods
NAME                     READY   STATUS    RESTARTS   AGE
my-release-zookeeper-0   1/1     Running   0          43m
my-release-kafka-0       1/1     Running   0          43m
my-redis-replicas-0      0/1     Running   0          40s
my-redis-master-0        1/1     Running   0          40s
```


## Clone this repo

```
$ git clone https://github.com/Nachimak28/realtime-analytics-on-streaming-data
# change directory to be inside the repo folder
$ cd realtime-analytics-on-streaming-data
```

## Deploy basic config for infra before every other deployment
There is a common config present which is shared by multiple containers and that must be deployed before other deployments

```
# change directory to be in the infra folder
$ cd infra
# now you are in the realtime-analytics-on-streaming-data/infra folder

# now create the config map
$ kubectl apply -f config_map.yaml
```

Output should look something like this:
```
configmap/streaming-config created
```

## Running the producer in the k3s cluster
This is a simple python random number generator pushing values to a kafka topic/queue mimicking/simulating actual sensor values received from a sensor (eg: nitrogen content soil sensor) at certain time intervals (10 seconds in our case)

```
# from the previous step, you were in the infra directory
# change directory to be in the producer directory
cd ../producer
# now you must be in the reaimtime-analytics-on-streaming-data/producer directory
```

Build the docker image and tag it
Note: the localhost:5000 URL might change if you're working with public docker hub or a private cloud registry. 
```
docker build -t localhost:5000/pykaf-producer:v1 .
```

Push the image to the registry for k3s to pick it up
```
docker push localhost:5000/pykaf-producer:v1
```

Once pushed, deploy the producer in the cluster
If you're using a private docker image registry please do not forget to put the right image name in the kubernetes yaml file (deploy.yaml) at line number 25 and then use the following command.
```
$ kubectl apply -f deploy.yaml
```
The output must be something like this
```
deployment.apps/pykaf-producer created
```

Test if the deployment is running without any errors:
```
$ kubectl get pods | grep pykaf # filtering by deployment name
```
Output should looks something like this:
```
NAME                              READY   STATUS    RESTARTS      AGE
pykaf-producer-5798b957d5-t29pv   1/1     Running   0             89s
```
## Running the consumer in the k3s cluster
This is the piece of code responsible for the consumption of data from the kafka topic/queue and doing the necessary calculations.

The calculations done are for the moving mean and standard deviation and this consumer is also responsible for writing the data to the redis db for the necessary CRUD operations.

The steps to deploy this consumer are similar to the producer codebase
```
# from the previous step you must be in the producer directory
# change directory to the consumer folder
$ cd ../consumer
# now you must be in the realtime-analytics-on-streaming-data/consumer directory
```

Build the docker file, tag it and push it to the registry
```
$ docker build -t localhost:5000/pykaf-consumer:v1 .
$ docker push localhost:5000/pykaf-consumer:v1
```

Deploy in the cluster
```
$ kubectl apply -f deploy.yaml
# output
deployment.apps/pykaf-consumer created
```

Test if the deployment is running without any errors:
```
$ kubectl get pods | grep pykaf
```

Output should looks something like this:
```
pykaf-producer-5798b957d5-t29pv   1/1     Running   0             15m
pykaf-consumer-77bd8764f7-45578   1/1     Running   0             2m19s
```

The consumer codebase is responsible for:
* Listening to a kafka topic to consume messages from the so-called sensor/producer
* Doing the calculations for moving mean and standard deviation
* Reading & Updating the calculation output to redis
* Producing or transmitting calcultion results to another kafka topic/queue for the backend to consume and produce them to a nifty little frontend for the real time updates

## Testing the event flow between the producer and consumer flow
Now that our kafka, producer and consumer codebases are deployed lets verify if the events are being transmitted among them successfully.

Run the following command to check the pod names of the producer and consumer deployments
```
$ kubectl get pods | grep pykaf
# output
pykaf-producer-5798b957d5-t29pv   1/1     Running   0             15m
pykaf-consumer-77bd8764f7-45578   1/1     Running   0             2m19s
```

Now we'll view the logs of both the pods simultaneously to see the event transmission happening. We should ideally use two terminal windows/tabs to view the logs.


In terminal window 1
```
# copy the pod name of the producer (here we have it as pykaf-producer-5798b957d5-t29pv, you might see a different name) and execute the following commmand
$ kubectl logs pykaf-producer-5798b957d5-t29pv -f

# output
# press Ctrl + c to escape from these streaming logs
message published
message published
message published
message published
message published
message published
```

In terminal window 2
```
# copy the pod name of the consumer (here we have it as pykaf-consumer-77bd8764f7-45578, you might see a different name) and execute the following commmand

$ kubectl logs pykaf-consumer-77bd8764f7-45578 -f

# output
# press Ctrl + c to escape from these streaming logs
Message is None
Message is None
Message is None
Message is None
Message is None
b'{"2022-07-17_15-43-10": {"value": 0.6809525757404139, "sensor": "sensor_1"}}'
Data updated successfully
{'mean': 0.5077522295687356, 'std_dev': 0.29110740241655597, 'pre_division_variance': 20.592675297236664, 'variance': 0.08474351974171467, 'stream_length': 244.0}
Message is None
Message is None
Message is None
Message is None
```
If you see these bytes encoded string (dictionary) data in the satreaming logs every 10 seconds, your event transmission is running perfectly.

What if it isn't running perfectly and I do not see data on the producer or consumer side ?
Answer: It could be a problem in the kafka config - kafka cluster name, queue name etc only if modified. If this code is run without any modifications, then there ideally should not be any errors or missing data.


## Deploying the socketio backend in the k3s cluster and creating the service
Now that the event transmission is successful, we need to deploy a backend service which listens to the consumer as it relays the results for the real time updates.
This backend is essentially a node, express server with a socketio integration which emits the events received from the kafka queue to the frontend.
Note: Socket.io is not websocket by itself - Read [this](https://socket.io/docs/v4/) to understand the difference.

```
# after the consumer deployment, change directory to be inside the backend directory
$ cd ../backend
```

Build the docker image, tag it and deploy it to the cluster
```
$ docker build -t localhost:5000/backend:v1 .
$ docker push localhost:5000/backend:v1
$ kubectl apply -f deploy.yaml

# test if container is running
$ kubectl get pods | grep backend
# output
backend-6984c9dd89-fpmrn          1/1     Running   0              51s
```

Exposing the deployment as a service within the cluster 
We don't expose the deployment directly to the outside world and use ingress for that
```
$ kubectl expose deployment backend --type=ClusterIP --name=backend-service --port=80 --target-port=3000

# test if the service is up and running on port 80 (not 3000 because we've done the port forwarding in the command above)

$ kubectl get svc | grep backend

# output
backend-service                 ClusterIP   10.43.229.96    <none>        80/TCP                       58s
# do not worry about the IP here, its an internal IP
```

## Deploying the frontend in the k3s cluster and creating the service
The frontend is a socket.io client built using react js and has some basic animations to show the real time updates. We could have easily set up a REST based backend but then we wouldn't get any updates from server automatically without refreshing the page. 

```
# once backend is deployed, we now need to be in the frontend directory
$ cd ../frontend

# now we are in the realtime-analytics-on-streaming-data/frontend directory
```

Before deploying the frontend, we must make a small modification of the external IP for the machine at line number 6 in the App.js file in the path `frontend/src/App.js`.
Put your machine's external IP at line number 6. 
eg: const ip = '149.63.47.22'

If you're on a local machine, I think but url can be `localhost` - untested assumption, feel free to check it out

Once the IP is changed, we can deploy the frontend just like the previous deployments

Build the docker image, tag it and push it to the registry

```
$ docker build -t localhost:5000/frontend:v1 .
$ docker push localhost:5000/frontend:v1
$ kubectl apply -f deploy.yaml
```

Expose the service as a ClusterIP service on port 80
```
$ kubectl expose deployment frontend --type=ClusterIP --name=frontend-svc --port=80 --target-port=3000
```

Test if the service exposed
```
$ kubectl get svc | grep front

# output
frontend-svc                    ClusterIP   10.43.189.53    <none>        80/TCP                       13s
```


## Depoying the ingress for the apps to be available outside the machine
Although we've created the services for our backend and frontend deployments, they're still available from within the cluster and not to the outside world. 
To make them accessible from the browser/postman we use a kubernetes network object called Ingress which manages the routing and the incoming/outgoing traffic to the necessary services based on their URL mapping. 
The ingress is make up of two components - an ingress controller and the ingress config. 
K3s already comes with an ingress controller configured and running - ```traefik```. A similar component is offered by nginx: ```ingress-nginx```which is the defacto standard while working with kubernetes. But here to avoid doing any new config, we simply use ```traefik``` because it offers similar capabilities as that of ```ingress-nginx```.

Assuming all the services are exposed we now go back into our infra folder 
```
$ cd ../infra
```

And deploy the ingress.yaml file which consists the routing instructions for our backend and frontend services
```
$ kubectl apply -f ingress.yaml
```
To verify if the ingress is running, run the following command

```
$ kubectl get ingress

# output
NAME            CLASS    HOSTS   ADDRESS       PORTS   AGE
nginx-ingress   <none>   *       <some-ip>     80      6s
```

Luckily in my cloud machine, I did not have to do any host or port binding of my VM to the ingress because I think k3s takes care of it. 
So get the external IP of your cloud machine and go to the following URL in your browser

http://<external-ip>/frontend

For a local deployment: just go to http://localhost/frontend

Voila!!
We're done here.


## Output

https://user-images.githubusercontent.com/23210132/179419520-fbf4ae49-5846-4099-a924-761125fbe336.mov

Note: The result will look similar for your deployment but the values might vary since the producer is a random number generator.

## Rejoice
Congratulations on making it till this far. We're done with the deployment and we can enjoy the output displayed in the browser.


## Word of caution
This is by no means a production level codebase and system design. If running locally, this system might slow down your computer if multiple other applications are already running.

## Some measures taken to have better security
Although this codebase isn't production grade, some measures can be taken to strengthen the security as follows:

* Authentication and RBAC for deployments for kafka
* RBAC for redis
* Making the python codebase asyncronous to have some thread-safe behaviour
* Configure TLS certificates in the ingress for the URLs to load the website on https instead of http
* Some replicasets for kafka in case of pod failures, our redis deployment is already resilient because it is a replicaset
* For components like kafka and redis, it would be preferrable to use managed services on clouds or on respective providers if you do not want the management headache and if you're a small team with limited knowledge about maintaining these services

## What all could go wrong - single point of failures ? 
* Kafka serves as the backbone in this architecture, if that goes down, the entire contraption is useless
* Redis serves as the current state for the resultant calculation of the analytics. If that goes down, we won't be able to show the updates to the frontend

## Is this system architecture extensible ?
Absolutely it is. One can add more sensors and do minor backend and frontend modifications to add more data
Some possible applications which can be modelled based on this architecture:
* A cricbuzz like live score for sports
* A system to show views on insta reels as more and more people watch your reel (this would need some user specific analytics modifications and not a general analytics like we have)
* Have a machine learning usecase where the inference happens in the consumer code and the results are relayed back to the user if its a long running task without having to worry about API timeouts


## Helpful links
* [Socketio integration with kafkajs](https://stackoverflow.com/questions/66337792/how-do-i-connect-kafkajs-with-socket-io)
