var problemForms = document.getElementsByClassName("worksheet-problem-form");
// prevent the form from being submitted
for (i = 0; i < problemForms.length; i++) {
    problemForms[i].addEventListener("submit", function(event){
        event.preventDefault();
        checkAnswer(this);
    });
};

// https://stackoverflow.com/questions/42291370/csrf-token-ajax-based-post-in-a-django-project
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    };
};

function checkAnswer(form) {
    var userAnswerValue = form.elements["user_answer"];
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
        response = JSON.parse(xhr.responseText);
        console.log(response);
        problem = document.getElementById(response.HTML_id);
        problemID = Number(problem.id.slice(-1))
        if (response.result == 'correct') {
            problem.classList.add("checked_correct");
            problem.classList.remove("checked_incorrect");
        } else if (response.result == 'incorrect') {
            problem.classList.add("checked_incorrect");
            problem.classList.remove("checked_correct");
        }
    }
};
