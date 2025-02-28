import os
import zipfile
from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from flask_cors import CORS
from ai_generate import generate_images
from remove_bg import remove_background, replace_background

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow cross-origin requests for API integration

# Ensure directories exist
for folder in ["static", "static/generated", "templates"]:
    os.makedirs(folder, exist_ok=True)

@app.route("/")
def home():
    """Render the main HTML page for web users."""
    return render_template("index.html", generated_images=[])

@app.route("/background-removal")
def background_removal():
    """Render the background removal page for web users."""
    return render_template("remove_bg.html", removed_bg_image=None)

# ✅ New API Endpoint for Mobile Apps
@app.route("/api/generate", methods=["POST"])
def api_generate():
    """API endpoint to generate AI images."""
    data = request.json
    prompt = data.get("prompt", "")
    num_images = data.get("num_images", 1)
    style = data.get("style", "none")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    image_paths = generate_images(prompt, num_images, style)
    image_urls = [f"https://your-server.com/static/generated/{os.path.basename(path)}" for path in image_paths]

    return jsonify({"images": image_urls})

# ✅ New API Endpoint for Background Removal
@app.route("/api/remove_bg", methods=["POST"])
def api_remove_bg():
    """API endpoint to remove background from an image."""
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    input_path = os.path.join("static", "generated", file.filename)
    file.save(input_path)

    bg_option = request.form.get("bg_option", "transparent")
    custom_bg = request.files.get("custom_bg")
    output_path = remove_background(input_path)

    if bg_option == "custom" and custom_bg:
        bg_path = os.path.join("static", "generated", custom_bg.filename)
        custom_bg.save(bg_path)
        output_path = replace_background(output_path, bg_path)

    image_url = f"https://your-server.com/static/generated/{os.path.basename(output_path)}"
    return jsonify({"removed_bg_image": image_url})

@app.route("/generate", methods=["POST"])
def generate():
    """Render HTML page for AI-generated images (for web users)."""
    prompt = request.form.get("prompt", "")
    num_images = request.form.get("num_images", 1, type=int)
    style = request.form.get("style", "none")

    image_paths = generate_images(prompt, num_images, style)
    return render_template("index.html", generated_images=image_paths)

@app.route("/remove_bg", methods=["POST"])
def remove_bg():
    """Render HTML page for background removal (for web users)."""
    if "image" not in request.files:
        return "No file uploaded", 400

    file = request.files["image"]
    input_path = os.path.join("static", "generated", file.filename)
    file.save(input_path)

    bg_option = request.form.get("bg_option", "transparent")
    custom_bg = request.files.get("custom_bg")
    output_path = remove_background(input_path)

    if bg_option == "custom" and custom_bg:
        bg_path = os.path.join("static", "generated", custom_bg.filename)
        custom_bg.save(bg_path)
        output_path = replace_background(output_path, bg_path)

    return render_template("remove_bg.html", removed_bg_image=output_path)

@app.route("/download/<filename>")
def download_image(filename):
    """Download a single image file from the static/generated directory."""
    return send_from_directory("static/generated", filename, as_attachment=True)

@app.route("/download-all")
def download_all_images():
    """Download all generated images as a ZIP file."""
    zip_path = os.path.join("static", "generated_images.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for img_file in os.listdir("static/generated"):
            img_path = os.path.join("static/generated", img_file)
            zipf.write(img_path, arcname=img_file)

    return send_file(zip_path, as_attachment=True)

@app.route("/favicon.ico")
def favicon():
    """Serve the favicon.ico file."""
    favicon_path = os.path.join(app.static_folder, "favicon.ico")
    if os.path.exists(favicon_path):
        return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
