const express = require("express");
const http = require("http");
const socketIO = require("socket.io");
const PORT = 8080;

const app = express();
const server = http(app);
const io = socketIO(server);

app.use(express.static("public"));
io.on("connection", socket => {
  console.log(socket);
});

app.listen(PORT, "localhost", error => {
  if (error) console.log(error);
  else console.log("Server is listening on Port", PORT);
});
