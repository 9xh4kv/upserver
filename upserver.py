import argparse
import os
import ssl
from flask import Flask, request, render_template, send_from_directory, abort, url_for

app = Flask(__name__)

# Specify the upload folder
cur_dir = os.getcwd()

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:subpath>', methods=['GET', 'POST'])
def upload_file(subpath=''):
    message = None
    current_path = os.path.join(cur_dir, subpath)
    
    if os.path.isfile(current_path):
        return download_file(subpath)
    
    if request.method == 'POST':
        files = request.files.getlist('file')  # Retrieve multiple files
        uploaded_files = 0 
        for file in files:
            if file:
                # Save the uploaded file to the upload folder
                filename = os.path.join(current_path, file.filename)
                file.save(filename)
                uploaded_files += 1  # Increment the counter for each uploaded file
                print("Receiving file: " + filename)
        if uploaded_files > 0:
            message = f'{uploaded_files} file(s) uploaded successfully!\n'
        else:
            message = 'No files were uploaded.'
    
    items = []
    try:
        for item in os.listdir(current_path):
            item_path = os.path.join(subpath, item)
            if os.path.isdir(os.path.join(current_path, item)):
                items.append((item, 'folder'))
            else:
                items.append((item, 'file'))
    except FileNotFoundError:
        abort(404)  # Return a 404 error without traceback
    
    return render_template('upload.html', message=message, items=items, subpath=subpath)

@app.route('/<path:filename>')
def download_file(filename):
    try:
        return send_from_directory(cur_dir, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/<path:subpath>')
def navigate(subpath):
    current_path = os.path.join(cur_dir, subpath)
    if os.path.isdir(current_path):
        return upload_file(subpath)
    else:
        return download_file(subpath)

def main():
    parser = argparse.ArgumentParser(description='Run the upserver application.')
    parser.add_argument('port', type=int, help='Port number to run the server on')
    parser.add_argument('--https', action='store_true', help='Enable HTTPS with self-signed certificate')
    args = parser.parse_args()
    print("==================================================")
    if args.https:
        # Create a self-signed certificate if it doesn't exist
        print("HTTPS \033[32menabled\033[0m, running server with \033[32mSSL\033[0m.")
        print("==================================================")
        certfile = '/tmp/upserver.pem'
        if not os.path.exists(certfile):
            os.system(f'openssl req -x509 -out {certfile} -keyout {certfile} -newkey rsa:2048 -nodes -sha256 -subj "/CN=localhost"')

        # Run the app with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile)
        app.run(host='0.0.0.0', port=args.port, ssl_context=context)
    else:
        # Run the app without SSL
        print("HTTPS \033[31mdisabled\033[0m, running server \033[31mwithout encryption\033[0m.")
        print("==================================================")
        app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()