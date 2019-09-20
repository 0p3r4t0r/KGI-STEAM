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
    xhr.open('POST', form.action);
    var csrftoken = getCookie('csrftoken');
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    var formData = new FormData(form);
    for (var pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]);
    };
    xhr.send(formData);
    // Recieve the response
    xhr.onreadystatechange = function () {
        var DONE = 4; // readyState 4 means the request is done.
        var OK = 200; // status 200 is a successful return.
        if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
                console.log(xhr.responseText); // 'This is the returned text.'
            } else {
                console.log('Error: ' + xhr.status); // An error occurred during the request.
            }
        }
    };
};
