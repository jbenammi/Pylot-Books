from system.core.model import Model
import re
EMAILREGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
class BookReview(Model):
    def __init__(self):
        super(BookReview, self).__init__()

    def register_user(self, reginfo):
        errors = {}
        if len(reginfo['name']) < 2:
            errors.update({'name': 'The first name field must be at least two characters'})
        if len(reginfo['alias']) < 2:
            errors.update({'alias': 'The last name field must be at least two characters'})
        if not EMAILREGEX.match(reginfo['email']):
            errors.update({'email': 'The E-Mail must be a valid e-mail address'})
        if len(reginfo['password']) < 8:
            errors.update({'password': 'Password must be at least 8 characters'})
        elif not any(char.isdigit() for char in str(reginfo['password'])):
            errors.update({'password': 'Password must contain at least one number'})
        elif not any(char.isupper() for char in str(reginfo['password'])):
            errors.update({'password': 'Password must contain at least one uppercase letter'})
        if reginfo['confirmpass'] != reginfo['password']:
            errors.update({'confirmpass': 'The password confirmation does not match the password'})
        if len(errors) > 0:
            return errors
        else:
            query1 = "SELECT email FROM users WHERE email = :email"
            data1 = {"email": reginfo['email']}
            if not self.db.query_db(query1, data1):
                pw_hash = self.bcrypt.generate_password_hash(reginfo['password'])
                query = "INSERT INTO users(user_name, alias, email, password, created_on, updated_on) VALUES(:user_name, :alias, :email, :password, now(), now())"
                info = {
                "user_name": reginfo['name'],
                "alias": reginfo['alias'],
                "email": reginfo['email'],
                "password": pw_hash
                }
                self.db.query_db(query, info)
                return "registered"
            else:
                errors.update({'user_registered': 'This E-Mail is already registered'})
                return errors

    def login_user(self, loginfo):
        errors = {}
        if not EMAILREGEX.match(loginfo['email']):
            errors.update({'email2': 'The E-Mail must be a valid e-mail address'})
        if len(loginfo['password']) < 8:
            errors.update({'password2': 'Password must be at least 8 characters'})
        if len(errors) > 0:
            return errors
        else:
            query = "SELECT * FROM users WHERE email = :email LIMIT 1"
            data = {'email': loginfo['email']}
            user = self.db.query_db(query, data)
            if user == []:
                errors.update({'notreg': 'E-Mail is not registered.'})
                return errors
            else:
                if self.bcrypt.check_password_hash(user[0]['password'], loginfo['password']):
                    logged_info = {'logged_info':{'id': user[0]['id'], 'user_name': user[0]['user_name'], 'alias': user[0]['alias']}}
                    return logged_info
                else:
                    errors.update({'passmatch': 'Incorrect password entered for registered E-Mail.'})
                    return errors

    # This should get all the review information for a specific book
   
    def get_book_info(self, id):
        query = "SELECT books.id as b_id, title, auth_name FROM books LEFT JOIN authors ON books.author_id = authors.id WHERE books.id = :id"
        data = {'id': id}
        return self.db.query_db(query, data)

    def get_book_reviews(self, id):
        query = "SELECT books.id as b_id, title, auth_name, reviews.id as r_id, reviews.user_id as r_user_id, review, rating, reviews.created_on as review_date, users.id as u_id, alias FROM reviews LEFT JOIN books ON reviews.book_id = books.id LEFT JOIN users ON reviews.user_id = users.id LEFT JOIN authors ON books.author_id = authors.id WHERE books.id = :id ORDER BY reviews.created_on DESC"
        data = {'id': id}
        return self.db.query_db(query, data)

    def add_review_to_book(self, review):
        query = "INSERT INTO reviews(review, rating, created_on, updated_on, user_id, book_id) VALUES(:review, :rating, now(), now(), :user_id, :book_id)"
        data = {
                'review': review['review'],
                'rating': review['rating'],
                'user_id': review['user_id'],
                'book_id': review['book_id']
                }
        self.db.query_db(query, data)
        return review['book_id']

    def get_user_books(self, id):
        query = "SELECT books.id as b_id, title, reviews.id as r_id, users.id as u_id, alias, user_name, email FROM reviews LEFT JOIN books ON reviews.book_id = books.id LEFT JOIN users ON reviews.user_id = users.id WHERE users.id = :id"
        data = {'id': id}
        return self.db.query_db(query, data)

    def get_auth_list(self):
        query = "SELECT * from authors"
        return self.db.query_db(query)

    def add_new_book(self, info):
        author = ""
        book_id = ""
        if info['new_auth'] == "":
            author = info['cur_auth']
        else:
            query1 = "INSERT INTO authors(auth_name, created_on, updated_on) VALUES(:auth, now(), now())"
            data1 = {'auth': info['new_auth']}
            self.db.query_db(query1, data1)
            query2 = "SELECT id FROM authors ORDER BY created_on DESC LIMIT 1"
            author = self.db.query_db(query2)
        query3 = "INSERT INTO books(title, created_on, updated_on, author_id) VALUES(:title, now(), now(), :auth_id)"
        data3 = {
                'title': info['title'],
                'auth_id': author[0]['id']
                }
        self.db.query_db(query3, data3)
        query4 = "SELECT id from books ORDER BY created_on DESC LIMIT 1"
        book_id = self.db.query_db(query4)
        query5 = "INSERT INTO reviews(review, rating, created_on, updated_on, user_id, book_id) VALUES(:review, :rating, now(), now(), :user_id, :book_id)"
        data5 = {
                'review': info['review'],
                'rating': info['rating'],
                'user_id': info['user_id'],
                'book_id': book_id[0]['id']
                }
        self.db.query_db(query5, data5)
        return book_id[0]['id']

    def get_book_list(self):
        query = "SELECT * from books"
        return self.db.query_db(query)

    def get_recent_reviews(self):
        query = "SELECT books.id as b_id, title, review, rating, reviews.created_on as review_date, users.id as u_id, users.alias FROM reviews LEFT JOIN books ON reviews.book_id = books.id LEFT JOIN users ON reviews.user_id = users.id ORDER BY reviews.created_on DESC LIMIT 3"
        return self.db.query_db(query)

    def delete_review(self, id):
        query = "DELETE FROM reviews WHERE id = :id"
        data = {'id': id}
        return self.db.query_db(query, data)