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




# 메인에서 '마음공유' 버튼 클릭 후 url 입력했을 때!
# 유얄엘 요청은 /review (method는 get) 로 받지만 뿌리는 html은 detail임.
@app.route("/review", methods=["GET"])
def book_get():
    url = request.args.get('bUrl')  # get 요청 받아오는 방법 : request.arg.get('form의 name')
    # https%3A%2F%2Fsearch.shopping.naver.com%2Fbook%2Fcatalog%2F32467089683%3FNaPm%3Dct%253Dl7mysnhs%257Cci%253Dd227deb74b6ba5a8436201854d336741d7ccb875%257Ctr%253Dboksl%257Csn%253D95694%257Chk%253D71a0581f878b44a2e5c214424d595ac1724f4337
    # print(url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one(
        '#__next > div > div.bookCatalog_book_container__b3htO > div.bookCatalog_inner_container__JUfKQ > div.bookCatalog_book_catalog__yiiIc > div.bookCatalog_book_info_top__SUILS > div.bookSummary_book_summary__NsCmt > div.bookTitle_book_title__e3mof > div.bookTitle_title_area__fspvB > h2').text
    image = soup.select_one(
        '#__next > div > div.bookCatalog_book_container__b3htO > div.bookCatalog_inner_container__JUfKQ > div.bookCatalog_book_catalog__yiiIc > div.bookCatalog_book_info_top__SUILS > div.bookImage_book_image__myUU5 > div.bookImage_img_area__kiGb6 > div > img')['src']

    # print(title)
    # print('-----------')
    # print(image)

    # print(title, image)
    # return jsonify({'url':url, 'title':title, 'image':image})
    return render_template('detail.html', title=title, image=image)



# 마음공유 버튼 통해서 유알엘 입력 > 별점선택/리뷰작성 후 '등록하기'버튼 눌렀을 때!
@app.route("/review", methods=["POST"])
def book_post():
    image = request.form['image']       # post 요청 받아오는 방법 : request.form['form의 name']
    title = request.form['title']
    star = request.form['star']
    content = request.form['content']

    print(title, star, content)

    # len + 1을 하면 안된다. 만약 데이터를 삭제한 경우라면?
    num = (len(list(db.books.find({}, {'_id': False})))) + 1

    doc = {
        'bnum': num,
        'image': image,
        'title': title,
        'star': star,
        'content': content
    }

    db.books.insert_one(doc)

    return redirect('/')
    # return render_template('index.html')

# localhost:5000/1

@app.route('/<int:num>', methods=["GET"])
def book_read(num):
    # print(type(num))
    book = list(db.books.find(
        {'bnum':num},
        {'_id': False}
    ))
    print(num, book)
    # return jsonify({'book': book})
    return render_template('review.html', book=book)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

