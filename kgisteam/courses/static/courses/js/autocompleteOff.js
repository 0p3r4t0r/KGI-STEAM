window.addEventListener("DOMContentLoaded", function(event) {
    let inputs = document.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++) {
        inputs[i].setAttribute("autocomplete", "off");
    }
});
