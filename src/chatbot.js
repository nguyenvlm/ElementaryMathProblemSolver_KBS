const { spawn } = require("child_process");
const path = require("path");

module.exports = () => {
  var bot = spawn("python", ["./src/chatbot.py"], {
    stdio: ["pipe", "pipe", "ignore"]
  });

  process.on("beforeExit", () => {
    bot.kill();
  });

  bot.ask = function(question, cb) {
    bot.stdin.write(question + "\n", error => {
      if (error) console.log(error);
    });

    bot.stdout.once("data", msg => {
      cb(msg.toString());
    });
  };

  return bot;
};
