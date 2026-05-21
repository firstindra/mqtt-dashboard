const express    = require("express");
const http       = require("http");
const { Server } = require("socket.io");
const mqtt       = require("mqtt");
const config     = require("./config.json");

const BROKER_HOST = process.env.BROKER_HOST || config.BROKER_HOST;
const BROKER_PORT = process.env.BROKER_PORT || config.BROKER_PORT;
const TOPIC       = process.env.TOPIC       || config.TOPIC;
const WEB_PORT    = process.env.PORT        || 3000;

const app    = express();
const server = http.createServer(app);
const io     = new Server(server);

app.use(express.static("public"));

const mqttClient = mqtt.connect(`mqtt://${BROKER_HOST}:${BROKER_PORT}`);

mqttClient.on("connect", () => {
  console.log(`MQTT terhubung: ${BROKER_HOST}:${BROKER_PORT}`);
  mqttClient.subscribe(TOPIC, { qos: 1 });
});

mqttClient.on("message", (topic, message) => {
  try {
    const data = JSON.parse(message.toString());
    console.log("[DATA]", data);
    io.emit("sensor-data", data);
  } catch (e) {
    console.error("Gagal parse JSON:", e.message);
  }
});

mqttClient.on("error", (err) => {
  console.error("MQTT Error:", err.message);
});

server.listen(WEB_PORT, () => {
  console.log(`Website berjalan di http://localhost:${WEB_PORT}`);
});
