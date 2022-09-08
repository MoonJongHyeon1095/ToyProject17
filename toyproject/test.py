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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(
        'https://search.shopping.naver.com/book/search?bookTabType=BEST_SELLER&catId=50005542&pageIndex=1&pageSize=40&query=%EB%84%A4%EC%9D%B4%EB%B2%84%EB%8F%84%EC%84%9C&sort=REL',
        headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    bookranks = soup.select('#book_list > ul > li')

    all_Brank = list(db.bookrank.find({}, {'_id': False}))
    for book in all_Brank:
        db.bookrank.delete_one({'title': book['title']})



    count = 0
    for i in bookranks:
        count += 1
        if count > 3:
            break

        a = i.select_one(
            'div > a.bookListItem_info_top__VgpiO.linkAnchor > div.bookListItem_text_area__hF892 > div.bookListItem_title__X7f9_ > span')
        title = a.text.split('위')[1]
        rank = a.text.split('위')[0]
        writer = i.select_one(
            'div > a.bookListItem_info_top__VgpiO.linkAnchor > div.bookListItem_text_area__hF892 > div.bookListItem_detail__RBQ6x > span.bookListItem_author__fdjcn').text[
                 2:]
        publisher = i.select_one(
            'div > a.bookListItem_info_top__VgpiO.linkAnchor > div.bookListItem_text_area__hF892 > div.bookListItem_detail__RBQ6x > span.bookListItem_detail_publish__FgPYQ > span:nth-child(1)').text[
                    2:]

        doc = {
            'rank': rank,
            'title': title,
            'writer': writer,
            'publisher': publisher

        }
        db.bookrank.insert_one(doc)


    last_rank = list(db.bookrank.find({}, {'_id': False}))
    books = list(db.books.find({}, {'_id': False}))

    print(books)
    # return jsonify({'books':books})
    return render_template('test1.html', books=books, ranks=last_rank)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)