
from system.core.controller import *
import datetime

class BookReviews(Controller):
    def __init__(self, action):
        super(BookReviews, self).__init__(action)
        self.load_model('BookReview')
        self.db = self._app.db

    def index(self):
        return self.load_view('index.html')

    def login(self):
        login_info = self.models['BookReview'].login_user(request.form)
        print login_info
        if 'logged_info' in login_info:
            session['logged_info'] = login_info['logged_info']
            return redirect('/dashboard')
        else:
            flash(login_info)
            return redirect('/')

    def register(self):
        reg_info = self.models['BookReview'].register_user(request.form)
        if reg_info == "registered":
            flash({'registered': "Thank you for registering, please log in."})
        else:
            flash(reg_info)
        return redirect('/')

    def dashboard(self):
        book_list = self.models['BookReview'].get_book_list()
        recent_reviews = self.models['BookReview'].get_recent_reviews()
        return self.load_view('dashboard.html', book_list = book_list, recent_reviews = recent_reviews)

    def book(self, id):
        book_reviews = self.models['BookReview'].get_book_reviews(id)
        book_info = self.models['BookReview'].get_book_info(id)
        print book_info
        return self.load_view('book.html', book_reviews = book_reviews, book_info = book_info)

    def add_review_book(self):
        book_review = self.models['BookReview'].add_review_to_book(request.form)
        return redirect('/book/'+ book_review)

    def view_user(self, id):
        book_list = self.models['BookReview'].get_user_books(id)
        total = len(book_list)
        return self.load_view('user.html', book_list = book_list, total = total)

    def view_add_book(self):
        auth_list = self.models['BookReview'].get_auth_list()
        return self.load_view('add_book.html', auth_list = auth_list)

    def add_new_books(self):
        book_id = self.models['BookReview'].add_new_book(request.form)
        return redirect('/book/' + str(book_id))

    def delete_reviews(self, id):
        book_id = self.models['BookReview'].delete_review(id)
        return redirect('/dashboard')

    def logout(self):
        session.clear()
        return redirect('/')

