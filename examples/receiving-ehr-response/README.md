### Receiving an EHR Response

![alt text](../../diagrams/out/data-flow.drawio.svg "Architecture diagram")

See more documentation on confluence: https://gpitbjss.atlassian.net/wiki/spaces/TW/pages/1936687128/Handover+Documentation#Step-5.-GP2GP-Response-(EHR)

It is recommended to go through the `pds-query` example first to get an initial understanding of how the SPINE works and how to setup connectivity

To start:
* load the `postman_collection.json` and `postman_environment` files in Postman - in this example we're going to use the requests from the `GP2GP Health Record` subfolder

#### Using MHS Adapter to receive a message
* Follow instructions here: https://github.com/nhsconnect/integration-adaptor-mhs/blob/develop/mhs/running-mhs-adaptor-locally.md - Note that the client cert, client key and CA certs need to be provided as string (with the BEGIN and END lines).

* Send an EHR Extract response to the `inbound` component - use the `EHR Extract to MHS inbound` query. The response should be an acknoledgement of receiving - will contain a line: ` <eb:Action>Acknowledgment</eb:Action>` 

* Check that [RabbitMQ](http://localhost:15672/#/queues) has queue with the name `inbound` and one message inside. Use the user interface of RabbitMQ to investigate more (like read the content of the message)

Notes: 
* On the AWS deployment, we will use [AmazonMQ](https://aws.amazon.com/amazon-mq) as a message broker (which is [ActiveMQ](http://activemq.apache.org/) deployment maintained by AWS)


#### Using GP2GP Adaptor to process the message
* Follow instructions here to get it running locally: https://github.com/nhsconnect/prm-deductions-gp2gp-adaptor
  - make sure the following env are set in the `.env` file (along side the others already there):
  ```
  AUTHORIZATION_KEYS=auth-key-1
  MHS_OUTBOUND_URL=http://localhost:80
  DEDUCTIONS_ASID=918999199177
  ```
* Enable STOMP protocol for RabbitMQ (see notes on explanation) by applying the git patch `enable_stomp_for_rabbit.patch` onto the `integration-adaptor-mhs` repo. Restart the RabbitMQ container for the changes to take effect and check on the RabbitMQ UI if the plugin is enabled (http://localhost:15672 `Ports and contexts` section)

* Use the `fixes-to-work-locally` branch of the GP2GP adaptor (assumption is that very soon those changes will be integrated on master - check that's the case and update this entry is it is)

* Update the `.env` file to contain the following lines which points the GP2GP to the RabbitMQ instance:
```.env
MHS_QUEUE_NAME=inbound
MHS_QUEUE_URL_1=amqp://localhost:61613
MHS_QUEUE_URL_2=amqp://localhost:61613
MHS_QUEUE_VIRTUAL_HOST=/
MHS_QUEUE_USERNAME=guest
MHS_QUEUE_PASSWORD=guest
```

* Start GP2GP locally: `npm run start:local`

* Send an EHR Extract response to the inbound component - use the `EHR Extract to MHS inbound` query. The response should be an acknoledgement of receiving

* In RabbitMQ the expectation is that the total number of messages of the `inbound` queue is increased by 1 and that there are no pending messages

* Because the EHR Repo is not running - the GP2GP Adaptor will not successfully process the message and associated errors will appear in the logs. Expected errors: `failed to get pre-signed url` and `failed to store message to ehr repository`

Notes:
* GP2GP uses the [STOMP](https://stomp.github.io/) protocol which is not enable by default in the setup provided in the `integration-adaptor-mhs` repo. The patch above exposed the STOMP port on the host and enables the plugin for Rabbit (see https://hub.docker.com/_/rabbitmq `Enable plugins` section)

#### Using EHR Repo to store the message