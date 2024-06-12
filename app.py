from flask import Flask, request, send_from_directory, render_template, jsonify
import os
import json
import subprocess

app = Flask(__name__)
FONT_FOLDER = os.path.join(app.static_folder, 'fonts')
MAPPING_FILE = 'font_mappings.json'
UPLOAD_FOLDER = 'uploads'
STARTER_FONT_FILE_PATH = 'path_to_your_starter_font_file.ttf'
FONT_FILE_NAME = 'updated_font'


def call_ffpython(script_path, mode):
    # Path to the ffpython.exe (modify this to the correct path)
    # ffpython_path = r'C:\Users\kanan\OneDrive\Desktop\Work\Pyy\test\deps\bin\ffpython.exe'
    ffpython_path = os.path.join('deps/bin', 'ffpython.exe')
    # Ensure the path exists
    if not os.path.exists(ffpython_path):
        raise FileNotFoundError(f"ffpython.exe not found at {ffpython_path}")

    # Call ffpython.exe with the script as an argument
    def run_script():
        try:
            result = subprocess.run([ffpython_path, script_path, mode], check=True, capture_output=True, text=True)
            print("Output:", result.stdout)
            # callback()
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)

    run_script()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the font
FONT = fontforge.open(STARTER_FONT_FILE_PATH)

# Function to load the font mappings from the JSON file
def load_mappings():
    with open(MAPPING_FILE, 'r') as f:
        return json.load(f)

# Function to save the font mappings to the JSON file
def save_mappings(data):
    with open(MAPPING_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def save_new_font():
    global FONT
    FONT.generate(os.path.join(FONT_FOLDER, f"{FONT_FILE_NAME}.ttf"))
    FONT.generate(os.path.join(FONT_FOLDER, f"{FONT_FILE_NAME}.eot"))
    FONT.generate(os.path.join(FONT_FOLDER, f"{FONT_FILE_NAME}.woff"))
    FONT.generate(os.path.join(FONT_FOLDER, f"{FONT_FILE_NAME}.woff2"))

@app.route('/update_glyph_name', methods=['POST'])
def update_glyph_name():
    data = request.json
    font_name = data.get('font_name')
    old_glyph_name = data.get('old_glyph_name')
    new_glyph_name = data.get('new_glyph_name')
    
    # Load the current font mappings
    fonts = load_mappings()
    
    if font_name not in fonts:
        return jsonify({"error": "Font not found"}), 404
    
    if 'glyphs' not in fonts[font_name]:
        return jsonify({"error": "Glyphs not found"}), 404
    
    glyphs = fonts[font_name]['glyphs']
    
    # Find the glyph with the old name and update it
    glyph_found = False
    for glyph in glyphs:
        if glyph['glyph_name'] == old_glyph_name:
            glyph['glyph_name'] = new_glyph_name
            glyph_found = True
            break
    
    if not glyph_found:
        return jsonify({"error": "Glyph not found"}), 404
    
    # Save the updated mappings to the JSON file
    save_mappings(fonts)
    
    return jsonify({"message": "Glyph name updated successfully"}), 200

@app.route('/replace_glyph', methods=['POST'])
def replace_glyph():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    codepoint = request.form.get('codepoint')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.svg'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        try:
            replace_glyph_in_font(filepath, codepoint)
            save_new_font()  # Save the new font files
            return jsonify({"message": "Glyph replaced and font updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

def replace_glyph_in_font(filepath, codepoint):
    global FONT
    glyph_code = 'uni' + format(int(codepoint), '04X')
    glyph = FONT[glyph_code]
    glyph.clear()
    glyph.importOutlines(filepath)
    glyph.correctDirection()

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

@app.route('/get_font_data', methods=['GET'])
def get_font_data():
    font_name = request.args.get('name')
    fonts = load_mappings()
    if font_name not in fonts:
        return jsonify({"error": "Font not found"}), 404
    return jsonify(fonts[font_name]), 200

if __name__ == '__main__':
    app.run(debug=True)
