import "jquery";
import "bootstrap";

import io from "socket.io-client";

var socket = io();

var card_template = `<div class="card">
  <div class="card-header p-0">
    <a data-toggle="collapse" data-target="#{{ id }}" aria-expanded="false" aria-controls="{{ id }}">
      {{ question }}
    </a>
  </div>

  <div id="{{ id }}" class="collapse" data-parent="#messages-view">
    <div class="card-body">
      {{ answer }}
    </div>
  </div>
</div>`;

socket.on("connect", () => {
  console.log("Connected to Server");
});

socket.on("answer", msg => {
  var box = $("#messages-view");

  var card = card_template
    .replace(/{{ id }}/g, msg.id)
    .replace(/{{ question }}/g, msg.question)
    .replace(/{{ answer }}/g, msg.answer.replace("\n", "<br />"));

  box.append(card);
});

$("#chatbox").submit(event => {
  event.preventDefault();

  var value = $("#message")
    .val()
    .trim();

  if (value != "") {
    socket.emit("ask", {
      id: id_generator(),
      question: value
    });
  }
  $("#message").val("");
});

// Autoresize message Input area
(function() {
  var msgInp = $("#message");
  var msgBtn = $("#chatbox #outbound button");

  function resize() {
    msgInp.css("height", "40px");
    msgInp.css("height", msgInp[0].scrollHeight + "px");

    msgBtn.css("height", "40px");
    msgBtn.css("height", msgInp[0].scrollHeight + "px");
  }
  /* 0-timeout to get the already changed msgInp */
  function delayedResize() {
    window.setTimeout(resize, 0);
  }

  msgInp.on("change", resize);
  msgInp.on("cut", delayedResize);
  msgInp.on("paste", delayedResize);
  msgInp.on("drop", delayedResize);
  msgInp.on("keydown", event => {
    if (event.keyCode == 13) {
      event.preventDefault();

      if (event.ctrlKey) {
        event.target.value = event.target.value + "\n";
      } else {
        $("#chatbox").submit();
      }
    }
    delayedResize();
  });

  msgInp.focus();
  msgInp.select();
  resize();
})();

function id_generator() {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return (
    "_" +
    Math.random()
      .toString(36)
      .substr(2, 9)
  );
}
