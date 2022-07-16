const { Kafka } = require("kafkajs");
const clientId = "my-app";
const brokers = ["my-release-kafka.default.svc.cluster.local:9092"];
const topic = "frontup";

const kafka = new Kafka({ clientId, brokers });
// create a new consumer from the kafka client, and set its group ID
// the group ID helps Kafka keep track of the messages that this client
// is yet to receive
const consumer = kafka.consumer({ groupId: clientId });

const consume = async (cb) => {
  // first, we wait for the client to connect and subscribe to the given topic
  await consumer.connect();
  await consumer.subscribe({ topic });
  await consumer.run({
    // this function is called every time the consumer gets a new message
    eachMessage: ({ from, to, message }) => {
      cb({ from, to, message });
    },
  });
};

module.exports = consume;
