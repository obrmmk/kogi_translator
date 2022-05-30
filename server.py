from doctest import OutputChecker
import gdown
import os
import subprocess
from flask import Flask, render_template, request
import modules

try:
    import sentencepiece
except ModuleNotFoundError:
    os.system('pip install sentencepiece')

try:
    import transformers
except ModuleNotFoundError:
    os.system('pip install transformers')

import torch
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
# from google_drive_downloader import GoogleDriveDownloader

USE_GPU = torch.cuda.is_available()
DEVICE = torch.device('cuda:0' if USE_GPU else 'cpu')
print('DEVICE :', DEVICE)

 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post():
    try:
        if request.form['text']:
            input = request.form['text']
            model_id = '1ejyg2VzwA-MbaXANmLALYBUfV4iD3_W1'
            nmt = modules.nlpcode.compose_nmt(modules.t5.generate_nmt(model_id=model_id))
            cached = {'':''}
            ss=[]
            for line in input.split('\n'):
                if line not in cached:
                    translated = nmt(line, beams=1)
                    print(line, '=>', translated)
                    cached[line] = translated
                else:
                    translated = cached[line]
                ss.append(translated)
            output = '\n'.join(ss)
            # return render_template('index.html', input=format(input))
            return render_template('index.html', output=format(output))
    except:
        return render_template('index.html')

if __name__ == '__main__':

    app.debug = True
    app.run(host='localhost', port=8888)
