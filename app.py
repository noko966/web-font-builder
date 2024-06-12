from flask import Flask, request, send_from_directory, render_template, jsonify
import os
import json

app = Flask(__name__)
FONT_FOLDER = os.path.join(app.static_folder, 'fonts')
MAPPING_FILE = 'font_mappings.json'

# Function to load the font mappings from the JSON file
def load_mappings():
    with open(MAPPING_FILE, 'r') as f:
        return json.load(f)

# Function to save the font mappings to the JSON file
def save_mappings(data):
    with open(MAPPING_FILE, 'w') as f:
        json.dump(data, f, indent=4)

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
