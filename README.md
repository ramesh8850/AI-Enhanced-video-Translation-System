# AI-Enhanced Video Translation System

## Overview

The **AI-Enhanced Video Translation System** is a web application that enables users to upload videos or provide YouTube links for translation into selected languages. The system processes the video to extract audio, converts it to text, translates the text, and then synthesizes the translated audio back into the video. This project aims to improve accessibility and understanding of video content across different languages.

## Features

- Upload video files or input YouTube links.
- Select target language for translation.
- Audio extraction and transcription using AI techniques.
- Text translation with high accuracy.
- Merging translated audio back into the original video.
- Downloadable translated videos.

## Technologies Used

- Python
- Flask
- FFmpeg (for audio and video processing)
- Googletrans (for text translation)
- Hugging Face Transformers (for speech recognition using Whisper Small)
- Pydub (for audio processing)
- MoviePy (for video editing)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name

## Install the required dependencies:

### bash
- pip install -r requirements.txt
- FFmpeg Installation: Make sure you have FFmpeg installed on your machine. Follow the instructions in the link to set it up.

## Usage
- Start the Flask application:

### bash
- python server.py
- Open your browser and navigate to http://localhost:5000.

- Upload your video file or enter a YouTube link, select the target language, and click "Translate."

- Once processing is complete, you can download the translated video.
## Interface
- ![video_translation ouput](https://github.com/user-attachments/assets/b929aafa-2abd-4f54-ae3e-48b82891315d)


## Contributing
- Contributions are welcome! If you have suggestions for improvements or want to report bugs, please create an issue or submit a pull request.

## License
- This project is licensed under the MIT License. See the LICENSE file for details.
