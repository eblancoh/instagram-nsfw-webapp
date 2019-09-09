# import the Flask class from the flask module
import os
from os import urandom
import requests
from flask import Flask, redirect, render_template, request, url_for, jsonify, session
from app_suggested import PrivateIGScrapper, nsfw_api_batch_post

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/', methods=['GET', 'POST'])
def login():
    credentials = {}
    if request.method == 'POST':
        try:
            session['username'] = request.form['username']

            credentials['username']=request.form['username']
            credentials['password']=request.form['password']
            credentials['target']=request.form['target']
            
            scraper = PrivateIGScrapper(username=credentials['target'], 
                                        login_user=credentials['username'], 
                                        login_pass=credentials['password'], 
                                        #driver='geckodriver')
                                        driver='chromedriver')

            images_urls, prof_pic, suggested = scraper.suggested_imgs_urls()

            preds = nsfw_api_batch_post(images_urls, 
                                        suggested,
                                        credentials['target'])

            print('Scrapping finished.')

            return render_template('report.html', 
            preds=preds, prof_pic=prof_pic, 
            target=credentials['target'])
            
        except Exception as e:
            return (str(e))
    return render_template('login.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    return render_template('report.html')

def to_login():
    return redirect(url_for('login'))
    
def sign_out():
    session.pop('username')
    return redirect(url_for('login'))

# start the server with the 'run()' method
if __name__ == '__main__':
    app.secret_key = urandom(24)
    app.run(host='localhost', debug=True)