# upserver/upserver.py
import argparse
from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Specify the upload folder
cur_dir = os.getcwd()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file to the upload folder
            filename = os.path.join(cur_dir, file.filename)
            file.save(filename)
            return 'File uploaded successfully!'
    return render_template('upload.html')

def main():
    parser = argparse.ArgumentParser(description='Run the upserver application.')
    parser.add_argument('port', type=int, help='Port number to run the server on')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)

if __name__ == '__main__':
    main()
