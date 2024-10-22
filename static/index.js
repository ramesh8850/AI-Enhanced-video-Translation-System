
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


// Display the selected video immediately upon choosing it
function displaySelectedVideo() {
    const fileInput = document.getElementById('videoFile');
    const uploadedVideoPlayer = document.getElementById('uploadedVideoPlayer');
    const uploadedVideo = document.getElementById('uploadedVideo');
    const uploadedVideoSource = document.getElementById('uploadedVideoSource');

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const videoURL = URL.createObjectURL(file);

        uploadedVideoSource.src = videoURL;
        uploadedVideo.load();  // Load the new video
        uploadedVideoPlayer.style.display = 'block';  // Show the uploaded video player
    }
}

// Attach the displaySelectedVideo function to the input element
document.getElementById('videoFile').addEventListener('change', displaySelectedVideo);

