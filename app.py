from flask import Flask, send_from_directory, render_template, jsonify
import os

app = Flask(__name__)
FONT_FOLDER = os.path.join(app.static_folder, 'fonts')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/fonts/<path:filename>')
def serve_font(filename):
    return send_from_directory(FONT_FOLDER, filename)

@app.route('/fonts')
def list_fonts():
    try:
        files = os.listdir(FONT_FOLDER)
        font_files = [f for f in files if f.endswith(('.ttf', '.eot', '.woff', '.woff2'))]
        return jsonify(font_files)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
