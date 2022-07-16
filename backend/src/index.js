// all module imports
const express = require("express");
const app = express();
const http = require("http");
const server = http.createServer(app);
const cors = require("cors");
app.use(cors());
const redis = require("redis");
require("dotenv").config();
const { Server } = require("socket.io");
const io = new Server(server, {
  cors: {
    origin: "*",
  },
  // path: "/be/socket.io",
  secure: false,
});
const consume = require('./consumer.js');



const redis_host = process.env.REDIS_HOST;
const redis_password = process.env.REDIS_PASSWORD;
const redis_username = 'default';
const redis_url = `redis://${redis_username}:${redis_password}@${redis_host}:6379/0`;
const client = redis.createClient({ url: redis_url });
client.connect();

client.on("error", (err) => {
  console.log("Error " + err);
});

// app.get("/initvalue", async (req, res) => {
//   // retrieve data from redis and send that
//   // await client.connect();
//   const value = await client.hGetAll("sensor_1");
//   if (value) {
//     res.send(value)
//   }
//   else {
//     res.send({message: 'error retrieving data from redis'})
//   }

//   // await client.disconnect();
// });


app.get("/be/initvalue", async (req, res) => {
  // retrieve data from redis and send that
  const value = await client.hGetAll("sensor_1");
  if (value) {
    res.send(value);
  } else {
    res.send({ message: "error retrieving data from redis" });
  }
});

consume(({ from, to, message }) => {
  value = JSON.parse(message.value.toString());
  console.log(value);
  io.sockets.emit("newMessage", value);
});


server.listen(3000, () => {
  console.log("listening on *:3000");
});