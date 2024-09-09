document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('videoFile');
    const languageSelect = document.getElementById('languageSelect');
    formData.append('videoFile', fileInput.files[0]);
    formData.append('language', languageSelect.value);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.success) {
            const downloadLink = document.getElementById('downloadLink');
            const translatedVideoLink = document.getElementById('translatedVideoLink');
            translatedVideoLink.href = result.downloadUrl;
            downloadLink.style.display = 'block';
        } else {
            alert('Error: ' + result.message);  // Display error message to user
        }
    } catch (error) {
        console.error('Error uploading video:', error);
        alert('Error uploading video: ' + error.message);  // Display error message to user
    }
});