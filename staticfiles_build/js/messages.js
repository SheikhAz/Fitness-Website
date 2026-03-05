window.addEventListener("load", function () {

  const messages = document.querySelectorAll(".flash-message");

  if (!messages.length) return;

  messages.forEach(function(message) {

    setTimeout(function () {

      // fade animation
      message.style.opacity = "0";
      message.style.transform = "translateY(-15px)";
      message.style.transition = "all 0.4s ease";

      // remove element
      setTimeout(function () {
        message.remove();
      }, 400);

    }, 3000); // 3 seconds

  });

});
