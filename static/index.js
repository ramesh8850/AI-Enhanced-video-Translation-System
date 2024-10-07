// document.getElementById('uploadForm').addEventListener('submit', async function(event) {
//     event.preventDefault();
//     const formData = new FormData();
//     const fileInput = document.getElementById('videoFile');
//     const languageSelect = document.getElementById('languageSelect');
//     formData.append('videoFile', fileInput.files[0]);
//     formData.append('language', languageSelect.value);

//     try {
//         const response = await fetch('/upload', {
//             method: 'POST',
//             body: formData
//         });
//         const result = await response.json();
//         if (result.success) {
//             const videoPlayer = document.getElementById('videoPlayer');
//             const translatedVideo = document.getElementById('translatedVideo');
//             const translatedVideoSource = document.getElementById('translatedVideoSource');

//             translatedVideoSource.src = result.downloadUrl;
//             translatedVideo.load();  // Load the new video source
//             videoPlayer.style.display = 'block';  // Show the video player
//         } else {
//             alert('Error: ' + result.message);  // Display error message to user
//         }
//     } catch (error) {
//         console.error('Error uploading video:', error);
//         alert('Error uploading video: ' + error.message);  // Display error message to user
//     }
// });

document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('videoFile');
    // const videoLinkInput = document.getElementById('videoLink');
    const languageSelect = document.getElementById('languageSelect');
    const loadingIndicator = document.getElementById('loadingIndicator'); // Add this line

    // Check if file is uploaded or a link is provided
    if (fileInput.files.length > 0) {
        formData.append('videoFile', fileInput.files[0]);
    } 
    // else if (videoLinkInput.value) {
    //     formData.append('videoLink', videoLinkInput.value);
    // } 
    else {
        alert('Please upload a video file or provide a YouTube link.');
        return;
    }

    formData.append('language', languageSelect.value);

    // Show loading indicator
    loadingIndicator.style.display = 'block'; 

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        // Hide loading indicator
        loadingIndicator.style.display = 'none';

        if (result.success) {
            const translatedVideo = document.getElementById('translatedVideo');
            const videoSource = document.getElementById('videoSource');
            videoSource.src = result.downloadUrl;
            translatedVideo.load();
            document.getElementById('videoPlayer').style.display = 'block';
            document.getElementById('downloadLink').style.display = 'block';
            translatedVideo.href = result.downloadUrl;  // Update download link
        } else {
            alert('Error: ' + result.message);  // Display error message to user
        }
    } catch (error) {
        loadingIndicator.style.display = 'none'; // Hide loading indicator
        console.error('Error uploading video:', error);
        alert('Error uploading video: ' + error.message);  // Display error message to user
    }
});

