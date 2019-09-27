import { getCookie } from '/static/kgisteam/js/getCookie.js'


var problemForms = document.getElementsByClassName("worksheet-problem-form");
// prevent the form from being submitted
for (i = 0; i < problemForms.length; i++) {
    problemForms[i].addEventListener("submit", function(event){
        event.preventDefault();
        checkAnswer(this);
    });
};


function checkAnswer(form) {
    // Create and send the request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", form.action);
    var csrftoken = getCookie("csrftoken");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    var formData = new FormData(form);
    xhr.send(formData);
    // Recieve the response
    xhr.onreadystatechange = function () {
        var DONE = 4; // readyState 4 means the request is done.
        var OK = 200; // status 200 is a successful return.
        if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
                updatePage(xhr);
            } else {
                console.log('Error: ' + xhr.status); // An error occurred during the request.
            }
        }
    };

    // Update the page
    function updatePage(xhr) {
        let response = JSON.parse(xhr.responseText);
        let problem = document.getElementById(response.HTML_id);
        let problemID = Number(problem.id.slice(-1))
        if (response.result == 'correct') {
            problem.classList.add("checked_correct");
            problem.classList.remove("checked_incorrect");
        } else if (response.result == 'incorrect') {
            problem.classList.add("checked_incorrect");
            problem.classList.remove("checked_correct");
        }
    }
};
