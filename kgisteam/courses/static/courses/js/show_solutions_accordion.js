var acc = document.getElementsByClassName("show_solution_accordion");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function() {
        /* Toggle between hiding and showing the active panel */
        var panel = this.nextElementSibling;
        if (panel.style.display === "block") {
            panel.style.display = "none";
            this.innerHTML="show solution";
        } else {
            panel.style.display = "block";
            this.innerHTML="hide solution";
        }
    });
}
