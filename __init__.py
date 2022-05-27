import os
from .t5 import generate_nmt
from .nlpcode import compose_nmt
from .log import trans_log
import uuid
import json
import time
import socket

try:
    import IPython
    from google.colab import output
    try:
        from slackweb import Slack     
    except ModuleNotFoundError:
        import os
        os.system('pip install slackweb')
        from slackweb import Slack     
except ModuleNotFoundError:
    pass


# ダミー関数

HTML_SIMPLE = '''
<textarea id="input" style="float: left; width: 48%; height:100px; font-size: large;"></textarea>
<textarea id="output" style="width: 48%; height:100px; font-size: large;"></textarea>
'''

HTML_NOBU = '''
<style>
.parent {
  background-color: #edebeb;
  width: 100%;
  height: 150px;
}
textarea {
  width: 100%; 
  box-sizing: border-box;  /* ※これがないと横にはみ出る */
  height:120px; 
  font-size: large;
  outline: none;           /* ※ブラウザが標準で付加する線を消したいとき */
  resize: none;
}
.box11{
//    padding: 0.5em 1em;
//    margin: 2em 0;
    color: #5d627b;
    background: white;
    border-top: solid 5px #5d627b;
    box-shadow: 0 3px 5px rgba(0, 0, 0, 0.22);
}
.box18{
  //padding: 0.2em 0.5em;
  //margin: 2em 0;
  color: #565656;
  background: #ffeaea;
  background-image: url(https://2.bp.blogspot.com/-u7NQvQSgyAY/Ur1HXta5W7I/AAAAAAAAcfE/omW7_szrzao/s800/dog_corgi.png);
  background-size: 150%;
  background-repeat: no-repeat;
  background-position： top right;
  background-color:rgba(255,255,255,0.8);
  background-blend-mode:lighten;
  //box-shadow: 0px 0px 0px 10px #ffeaea;
  border: dashed 2px #ffc3c3;
  //border-radius: 8px;
}
.box16{
    //padding: 0.5em 1em;
    //margin: 2em 0;
    background: -webkit-repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
    background: repeating-linear-gradient(-45deg, #f0f8ff, #f0f8ff 3px,#e9f4ff 3px, #e9f4ff 7px);
}
.box24 {
    position: relative;
    padding: 0.5em 0.7em;
    margin: 2em 0;
    background: #6f4b3e;
    color: white;
    font-weight: bold;
}
.box24:after {
    position: absolute;
    content: '';
    top: 100%;
    left: 30px;
    border: 15px solid transparent;
    border-top: 15px solid #6f4b3e;
    width: 0;
    height: 0;
}
</style>
<div class="parent">
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="input">日本語</label>
<textarea id="input" class="box16"></textarea>
</div>
<div style="float: left; width: 48%; text-align: right;">
<label class="box24" for="outout">Python</label>
<textarea id="output" class="box18 python" readonly></textarea>
</div>
</div>
'''

SCRIPT = '''
<script>
    var timer = null;
    var logtimer = null;
    document.getElementById('input').addEventListener('input', (e) => {
        var text = e.srcElement.value;
        if(timer !== null) {
            clearTimeout(timer);
        }
        if(logtimer !== null) {
            clearTimeout(logtimer);
        }
        timer = setTimeout(() => {
            timer = null;
            (async function() {
                const result = await google.colab.kernel.invokeFunction('notebook.Convert', [text], {});
                const data = result.data['application/json'];
                const textarea = document.getElementById('output');
                textarea.textContent = data.result;
            })();
        }, 600);  // 何も打たななかったら600ms秒後に送信
        logtimer = setTimeout(() => {
            logtimer = null;
            google.colab.kernel.invokeFunction('notebook.Logger', [text], {});
        }, 60*1000*1/2);  // 30秒
    });
</script>
'''

def print_nop(*x):
    pass


def run_corgi(nmt, delay=600, print=print_nop):
    session = str(uuid.uuid1())
    seq = 0
    logs = []
    cached = {'':''}
    HOST = 'slack.com'
    ID = 'T02NYCBFP7B'
    ID2 = 'B02NYD09PS5'
    ID3 = 'ZsOa00deFxNF2MoK1yLt9PdI'
    url = f'https://hooks.{HOST}/services/{ID}/{ID2}/{ID3}'
    slack = Slack(url)

    def convert(text):
        nonlocal seq
        try:
            ss = []
            for line in text.split('\n'):
                if line not in cached:
                    translated = nmt(line, beams=1)
                    print(line, '=>', translated)
                    cached[line] = translated
                    host = socket.gethostname()
                    ip = socket.gethostbyname(host)
                    
                    logs.append({
                        'user' : ip,
                        'time' : time.time(),
                        'index': seq,
                        'input': line,
                        'translated': translated,
                    })
                    seq += 1
                else:
                    translated = cached[line]
                ss.append(translated)
            text = '\n'.join(ss)
            return IPython.display.JSON({'result': text})
        except Exception as e:
            print(e)
        return e

    def logger(text):
        try:
            if len(logs) > 0:
                data = {
                    'session': session,
                    'logs': logs
                }
                # slack.notify(text = json.dumps(data, ensure_ascii=False))
                json_data = json.loads(json.dumps(data, ensure_ascii=False))
                for i in json_data['logs']:
                    i['session'] = json_data['session']
                    slack.notify(text = json.dumps(i, ensure_ascii=False))
                logs.clear()
        except Exception as e:
            print(e)
        return e

    output.register_callback('notebook.Convert', convert)
    output.register_callback('notebook.Logger', logger)
    display(IPython.display.HTML(HTML_NOBU))
    HTML = SCRIPT.replace('600', str(delay))
    display(IPython.display.HTML(HTML))


def corgi(model_id, delay=600, print=print_nop):
    nmt = compose_nmt(generate_nmt(model_id=model_id))
    run_corgi(nmt, delay=delay, print=print)

def start_abci_BASE_corgi():
    corgi(model_id='1ejyg2VzwA-MbaXANmLALYBUfV4iD3_W1')
    
def start_colab_BASE_corgi():
    corgi(model_id='1Q8kzdDSkQ6_nkjAAjxHYWLvOaYFjnRtO')
    
def start_abci_BASE_expt_corgi():
    corgi(model_id='16Dk9BLhk0BN1ZNfogtUXp5f1XeeBUAl9')

def start_colab_BASE_expt_corgi():
    corgi(model_id='1v2Fc7M6l3zTbb_JdDg_YjOmG7qgocIax') 

def start_abci_tuned_by_expt_corgi():
    corgi(model_id='1VhTVZoIa6RMGo3KX4fyqpoAO6ZJ7-p9_')

def start_colab_tuned_by_expt_corgi():
    corgi(model_id='1ghJkMA9JdY5dd66u0fYCP3HZFDat87jB')

def start_corgi():
    corgi(model_id='1nShnUt4gV-X2GCUU2d6A-QhKS0AvrXDA')
    
