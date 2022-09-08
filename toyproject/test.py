from flask import Flask, render_template, request, jsonify, redirect
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi
ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.j6ve73r.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)

@app.route('/')
def home():
    books = list(db.books.find({}, {'_id': False}))

    print(books)
    # return jsonify({'books':books})
    return render_template('test1.html', books=books)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)