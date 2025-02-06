// Terabox Folder File Counter
// Usage: log into terabox web app, open browser developer tools and paste following script

function folderFileCounter(folderPath, folderName) {
    var teraBoxListApi = "https://www.terabox.com/api/list?order=name&desc=0&" +
        "dir=" + encodeURIComponent(folderPath + folderName) +
        "&num=100000&page=1&showempty=0";

    fetch(teraBoxListApi, {
        method: 'get'
    })
        .then(response => response.json())
        .then(data => {
            console.log("Found folder with: " + data.list.length + " elements");
        })
        .catch(function (err) {
            // Error :(
            console.log("Oops.. Error: " + err);
        });
};

// Example usage
// Target terabox folder path
folderFileCounter(
    "/",
    "myfolderName"
);
