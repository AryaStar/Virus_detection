from flask import Flask, render_template
from flask import Flask,render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
from Predict import predict
import os

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename =='':
            return redirect(url_for('wrong'))
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'report',secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        # upload_path = str(upload_path)
        return redirect(url_for('result',path=f.filename))
    return render_template('index.html')


@app.route('/wrong')
def wrong():
    return render_template('wrong.html')


@app.route('/result/<path>/')
def result(path):
    result = predict('report/'+path)
    # return result
    return render_template('result.html',result=result)


if __name__ == '__main__':
    app.run(debug=True)
