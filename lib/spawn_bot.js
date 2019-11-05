const { spawn } = require("child_process");
const path = require("path");

module.exports = (py_file = "chatbot.py") => {
  var bot = spawn("python", [py_file], {
    stdio: ["pipe", "pipe", "ignore"]
  });

  bot.on("error", error => {
    console.error("Bot Error:", error);
  });

  bot.on("close", (code, signal) => {
    console.warn(`Bot Closed!\nCode: ${code}\nSignal:${signal}`);
  });

  process.on("beforeExit", () => {
    console.log("Kill bot");
    bot.kill();
  });

  bot.stdout.on("data", msg => {
    console.log(msg.toString());
  });

  bot.ask = function(question, cb) {
    bot.stdin.write(`${question}\n`, error => {
      if (error) console.log(error);
    });

    bot.stdout.once("data", msg => {
      cb(decodeURI(msg.toString()));
    });
  };

  return bot;
};
