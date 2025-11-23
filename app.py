from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import google.generativeai as genai

app = Flask(__name__)

# Use /tmp when running on Vercel (read/write allowed)
if os.environ.get("VERCEL"):
    UPLOAD_FOLDER = "/tmp"
else:
    UPLOAD_FOLDER = "uploads"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'mysecretkey123'

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No PDF selected')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Create folder only if needed
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save file to Vercel /tmp or local "uploads"
        file.save(filepath)

        pdf_text = read_pdf(filepath)
        suggestions = enhance_resume(pdf_text)
        flash('File successfully uploaded')

        return render_template('index.html', pdf_text=pdf_text, suggestions=suggestions)
    else:
        flash('Only PDF files are supported')
        return redirect(request.url)


def read_pdf(filepath):
    pdf_text = ""
    with open(filepath, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            pdf_text += page.extract_text() or ''
    return pdf_text


def enhance_resume(resume_text):
    return get_gpt_suggestions(resume_text)


def get_gpt_suggestions(resume_text):
    # Read API key from env (set in Vercel)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key is not configured on the server."

    genai.configure(api_key=api_key)

    prompt = f"""
    Analyze the following text to identify if it is resume or CV content. 
    If it is, provide additional skills or further suggestions in bullet points. 
    Ensure each suggestion is separated by a new line. 
    If the content is not related to a resume or CV, state "This content is not related to a resume or CV" 
    and briefly describe the type of content.

    Resume Text:
    {resume_text}

    Suggestions:
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Optional: log for debugging
        app.logger.exception("Gemini API error: %s", e)
        return "There was an error contacting the AI service. Please try again later."



# DO NOT RUN app.run() ON VERCEL
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)












# from flask import Flask, render_template, request, redirect, url_for, flash
# from werkzeug.utils import secure_filename
# import os
# from PyPDF2 import PdfReader
# import google.generativeai as genai  # Using Gemini

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads/'
# app.secret_key = 'mysecretkey123'  # Required for session-based flash messages

# ALLOWED_EXTENSIONS = {'pdf'}


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)

#     file = request.files['file']

#     if file.filename == '':
#         flash('No PDF selected')
#         return redirect(request.url)

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#         # Ensure upload folder exists
#         if not os.path.exists(app.config['UPLOAD_FOLDER']):
#             os.makedirs(app.config['UPLOAD_FOLDER'])

#         # Always save (overwrite if same name)
#         file.save(filepath)

#         # Proceed with normal flow
#         pdf_text = read_pdf(filepath)
#         suggestions = enhance_resume(pdf_text)
#         flash('File successfully uploaded')
#         return render_template('index.html', pdf_text=pdf_text, suggestions=suggestions)
#     else:
#         flash('Only PDF files are supported')
#         return redirect(request.url)


# def read_pdf(filepath):
#     pdf_text = ""
#     with open(filepath, 'rb') as file:
#         reader = PdfReader(file)
#         for page in reader.pages:
#             pdf_text += page.extract_text() or ''
#     return pdf_text


# def enhance_resume(resume_text):
#     return get_gpt_suggestions(resume_text)


# def get_gpt_suggestions(resume_text):
#     # Configure Gemini API
#     genai.configure(api_key="AIzaSyDmYWvRc1XeCuaNNsehWdWj4xAN3RoQTEc")  # <-- put your real key here

#     prompt = f"""
#     Analyze the following text to identify if it is resume or CV content. If it is, provide additional skills or further suggestions in bullet points. Ensure each suggestion is separated by a new line. If the content is not related to a resume or CV, state "This content is not related to a resume or CV" and briefly describe the type of content. Do not provide any suggestions if the content is unrelated to a resume or CV.
#     Resume Text:
#     \n\n{resume_text}\n\n
#     Suggested suggestions:
#     """

#     model = genai.GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content(prompt)

#     return response.text


# if __name__ == '__main__':
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
#     app.run(host="0.0.0.0", port=80)














