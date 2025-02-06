// Terabox Folder File Counter
// Usage: log into terabox web app, open browser developer tools and paste following script

function folderFileCounter(folderPath, folderName) {
    var teraBoxListApi = "https://www.terabox.com/api/list?order=name&desc=0&" +
        "dir=" + encodeURIComponent(folderPath + folderName) +
        "&num=100000&page=1&showempty=0";

    var getJSON = function (url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'json';
        xhr.onload = function () {
            var status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            } else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };

    getJSON(teraBoxListApi, (status, response) => {
        if (status == null) {
            console.log("Found folder with: " + response.list.length + " elements");
        } else {
            // Error :(
            console.log("Oops.. Error");
        }
    });
};

// Example usage
// Target terabox folder path
folderFileCounter(
    "/",
    "myfolderName"
)