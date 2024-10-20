from flask import Flask, render_template, request, jsonify
import subprocess
import uuid
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

streams = {}

@app.route('/')
def index():
    app.logger.info(f"Accessed root route: {request.url}")
    return render_template('index.html')

@app.route('/start_stream', methods=['POST'])
def start_stream():
    app.logger.info(f"Received start_stream request: {request.json}")
    data = request.json
    stream_id = str(uuid.uuid4())

    command = [
        'ffmpeg',
        '-re', '-stream_loop', '-1', '-f', 'lavfi',
        '-i', f"testsrc=size={data['resolution']}:rate={data['fps']}",
        '-f', 'lavfi', '-i', "sine=frequency=220:beep_factor=4",
        '-b:v', data['bitrate'],
        '-profile:v', 'main', '-pix_fmt', 'yuv420p',
        # '-vf', f"drawtext=fontsize=110:fontcolor=red:x=(w-text_w)/4:y=(h-text_h)/2:text='%{{pts\\:hms}} %{{n}}':timecode_rate={data['fps']}, drawtext=fontsize=50:fontcolor=black:x=(w-text_w)/2:y=h-60:text='{data['resolution']} | {data['bitrate']} | {data['fps']}'",
        '-c:v', 'libx264', '-c:a', 'aac',
        '-f', 'mpegts', data['url']
    ]

    app.logger.info(f"Constructed FFmpeg command: {' '.join(command)}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streams[stream_id] = {'process': process, 'data': data}
        app.logger.info(f"Stream started successfully. Stream ID: {stream_id}")
        return jsonify({'id': stream_id, 'data': data})
    except Exception as e:
        app.logger.error(f"Failed to start stream: {e}")
        return jsonify({'error': 'Failed to start stream'}), 500

@app.route('/stop_stream/<stream_id>', methods=['POST'])
def stop_stream(stream_id):
    app.logger.info(f"Received stop_stream request for stream ID: {stream_id}")
    if stream_id in streams:
        streams[stream_id]['process'].terminate()
        del streams[stream_id]
        app.logger.info(f"Stream {stream_id} stopped successfully")
        return jsonify({'success': True})
    app.logger.warning(f"Attempt to stop non-existent stream: {stream_id}")
    return jsonify({'success': False}), 404

@app.route('/streams', methods=['GET'])
def get_streams():
    app.logger.info("Received request to list all streams")
    stream_list = {id: stream['data'] for id, stream in streams.items()}
    app.logger.info(f"Returning list of {len(stream_list)} streams")
    return jsonify(stream_list)

@app.errorhandler(404)
def not_found(error):
    app.logger.error(f"404 error: {request.url}")
    return "404: Not Found", 404
