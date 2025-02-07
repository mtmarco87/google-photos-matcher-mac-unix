// Terabox Folder Compare
// Usage: log into terabox web app, open browser developer tools and paste following script

async function folderFileCounter(folderPath, folderName) {
    var teraBoxListApi = "https://www.terabox.com/api/list?order=name&desc=0&" +
        "dir=" + encodeURIComponent(folderPath + folderName) +
        "&num=100000&page=1&showempty=0";

    count = 0;
    try {
        var response = await fetch(teraBoxListApi);
        const data = await response.json();
        console.log("Found folder with: " + data.list.length + " elements");
        count = data.list.length;
    } catch (error) {
        // Error :(
        console.log("Oops.. problem with folder: " + folderPath + folderName + ". Error: " + error);
    }

    return count;
};

async function folderCompare(folderBasePath, foldersStructure) {
    var totalCount = 0;
    for (var folder of foldersStructure) {
        totalCount += await folderFileCounter(folderBasePath, folder);
    }

    console.log("Total files/folders found: " + totalCount);
}

// Example usage using filecount.py output (to automatize the check process)

// Replace foldersStructure with the folder structure output produced by filecount.py output
// Note: run the filecount.py script one level up from the folder you want to count, to get a relative foldersStructure
var foldersStructure = [];
await folderCompare("/", foldersStructure);
