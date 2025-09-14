import os
from werkzeug.utils import secure_filename
import uuid

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add unique identifier to avoid conflicts
        filename = str(uuid.uuid4()) + '_' + filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None
