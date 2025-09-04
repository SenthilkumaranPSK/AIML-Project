import os
import cv2
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, session, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
from detection import MalpracticeDetector
from utils import generate_pdf_report
import threading
import time

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "malpractice_detection_key_2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Global variables for monitoring state
detector = None
monitoring_active = False
malpractice_log = []
current_counts = {
    'hand_gestures': 0,
    'mobile_phone': 0,
    'talking': 0
}
video_source = None
monitoring_thread = None

@app.route('/')
def index():
    """Landing page with start monitoring options"""
    return render_template('index.html')

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """Initialize monitoring session"""
    global detector, monitoring_active, malpractice_log, current_counts, video_source
    
    # Reset session data
    malpractice_log = []
    current_counts = {
        'hand_gestures': 0,
        'mobile_phone': 0,
        'talking': 0
    }
    
    # Get video source from form
    use_local_video = request.form.get('use_local_video') == 'true'
    local_video_path = request.form.get('local_video_path', '')
    
    if use_local_video and local_video_path:
        if not os.path.exists(local_video_path):
            return jsonify({'error': 'Video file not found'}), 400
        video_source = local_video_path
    else:
        video_source = 0  # Default camera
    
    # Initialize detector
    detector = MalpracticeDetector()
    monitoring_active = True
    
    # Store session start time
    session['session_start'] = datetime.now().isoformat()
    
    return redirect(url_for('monitoring'))

@app.route('/monitoring')
def monitoring():
    """Live monitoring page"""
    if not monitoring_active:
        return redirect(url_for('index'))
    return render_template('monitoring.html')

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop monitoring session"""
    global monitoring_active
    monitoring_active = False
    
    # Store session end time
    session['session_end'] = datetime.now().isoformat()
    
    return redirect(url_for('summary'))

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generate video frames with detection overlays"""
    global detector, monitoring_active, malpractice_log, current_counts, video_source
    
    if not detector or not monitoring_active:
        return
    
    cap = cv2.VideoCapture(video_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    try:
        while monitoring_active:
            success, frame = cap.read()
            if not success:
                if isinstance(video_source, str):  # Local video file
                    # Loop the video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            # Process frame for malpractice detection
            processed_frame, detections = detector.process_frame(frame)
            
            # Log detections
            if detections:
                timestamp = datetime.now()
                for detection in detections:
                    detection_type = detection['type']
                    confidence = detection['confidence']
                    
                    # Update counts
                    current_counts[detection_type] += 1
                    
                    # Create log entry
                    log_entry = {
                        'timestamp': timestamp.isoformat(),
                        'type': detection_type,
                        'confidence': confidence,
                        'count': current_counts[detection_type]
                    }
                    
                    malpractice_log.append(log_entry)
                    
                    # Save snapshot
                    snapshot_filename = f"snapshot_{detection_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                    snapshot_path = os.path.join('snapshots', snapshot_filename)
                    cv2.imwrite(snapshot_path, processed_frame)
                    
                    log_entry['snapshot'] = snapshot_filename
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # Control frame rate
    
    finally:
        cap.release()

@app.route('/get_alerts')
def get_alerts():
    """Get recent alerts for live updates"""
    global malpractice_log, current_counts
    
    # Return last 10 alerts and current counts
    recent_alerts = malpractice_log[-10:] if len(malpractice_log) > 10 else malpractice_log
    
    return jsonify({
        'alerts': recent_alerts,
        'counts': current_counts,
        'total_events': len(malpractice_log)
    })

@app.route('/summary')
def summary():
    """Summary page with malpractice report"""
    global malpractice_log, current_counts
    
    session_start = session.get('session_start')
    session_end = session.get('session_end')
    
    # Calculate session duration
    duration = None
    if session_start and session_end:
        start_time = datetime.fromisoformat(session_start)
        end_time = datetime.fromisoformat(session_end)
        duration = str(end_time - start_time).split('.')[0]  # Remove microseconds
    
    return render_template('summary.html', 
                         malpractice_log=malpractice_log,
                         counts=current_counts,
                         session_start=session_start,
                         session_end=session_end,
                         duration=duration)

@app.route('/snapshot/<filename>')
def get_snapshot(filename):
    """Serve snapshot images"""
    snapshot_path = os.path.join('snapshots', filename)
    if os.path.exists(snapshot_path):
        return send_file(snapshot_path)
    return "Snapshot not found", 404

@app.route('/export_pdf')
def export_pdf():
    """Export malpractice report as PDF"""
    global malpractice_log, current_counts
    
    session_start = session.get('session_start')
    session_end = session.get('session_end')
    
    pdf_filename = generate_pdf_report(malpractice_log, current_counts, session_start, session_end)
    
    return send_file(pdf_filename, as_attachment=True, download_name='malpractice_report.pdf')

@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reset current session"""
    global monitoring_active, malpractice_log, current_counts
    
    monitoring_active = False
    malpractice_log = []
    current_counts = {
        'hand_gestures': 0,
        'mobile_phone': 0,
        'talking': 0
    }
    
    session.clear()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure snapshots directory exists
    os.makedirs('snapshots', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
