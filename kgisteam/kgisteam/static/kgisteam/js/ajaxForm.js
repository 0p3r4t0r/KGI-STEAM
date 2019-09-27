/*
*/
export default ajaxForm;
export { ajaxForm };


import { getCookie } from "/static/kgisteam/js/getCookie.js";

function ajaxForm(method, with_csrf, form, updateFunction) {
    // Declare variables
    let xhr;
    let csrftoken;
    let formData;
    // Create and send the request
    xhr = new XMLHttpRequest();
    xhr.open(method, form.action);
    if (with_csrf) {
        csrftoken = getCookie("csrftoken");
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
    formData = new FormData(form);
    xhr.send(formData);
    // Recieve the response
    xhr.onreadystatechange = function () {
        let DONE = 4;  // readyState 4 means the request is done.
        let OK = 200;  // status 200 is a successful return.
        if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
                updateFunction(xhr);
            } else {
                console.log("Error: " + xhr.status);
            }
        }
    } // end of function
} // end of function ajaxForm
