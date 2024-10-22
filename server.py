from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import logging
from pytube import YouTube  # Import pytube to handle YouTube links
from process_video import process_video  # Import the process_video function

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure directories
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'videoFile' not in request.files and 'videoLink' not in request.form:
        return jsonify(success=False, message="No file or link provided")

    language = request.form.get('language')
    if not language:
        return jsonify(success=False, message="No language selected")

    if 'videoFile' in request.files and request.files['videoFile'].filename != '':
        file = request.files['videoFile']
        # Save uploaded video file to UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        logger.info(f"Video uploaded and saved to {file_path}")
    elif 'videoLink' in request.form and request.form['videoLink']:
        video_link = request.form['videoLink']
        yt = YouTube(video_link)
        file_path = os.path.join(UPLOAD_FOLDER, f"{yt.title}.mp4")
        yt.streams.get_highest_resolution().download(output_path=UPLOAD_FOLDER, filename=f"{yt.title}.mp4")
        logger.info(f"Video downloaded from YouTube and saved to {file_path}")
    else:
        return jsonify(success=False, message="No valid video provided")

    # Dynamically generate the processed video file path
    translated_file_path = os.path.join(PROCESSED_FOLDER, f'translated_{os.path.basename(file_path)}')
    try:
        # Process the video file with the dynamic paths
        process_video(file_path, translated_file_path, target_language=language)
        logger.info(f"Video processing complete, saved to {translated_file_path}")

        # Check if the translated file was created successfully
        if os.path.exists(translated_file_path):
            return jsonify(success=True, downloadUrl=f'/download/{os.path.basename(translated_file_path)}')
        else:
            return jsonify(success=False, message="Processed video not found")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return jsonify(success=False, message=str(e))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
