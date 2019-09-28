/*
*/
export default ajaxRequest;
export { ajaxRequest };


function ajaxRequest(method, url, updateFunction) {
    // Declare variables
    let xhr;
    // Create and send the request
    xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.send();
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
