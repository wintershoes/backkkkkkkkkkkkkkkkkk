# editor : banyanrong
# time : 2024/6/23 14:55
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from app import create_app, db
from app.models.model import User, Book, Review
from datetime import date


class ReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username='testuser', password="123456", email="123@163.com", role="admin")
            book = Book(title='testbook', author="test", publisher="testor", publish_date=date.today(), isbn="123456", location="west", status="available")
            db.session.add(user)
            db.session.add(book)
            db.session.commit()
            self.user_id = user.user_id
            self.book_id = book.book_id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_add_review(self):
        response = self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        self.assertEqual(response.status_code, 201)

    def test_get_book_rating(self):
        self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        response = self.client.get(f'/api/reviews/books/{self.book_id}/rating')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["average_rating"], 5.0)

    def test_get_reviews(self):
        self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        response = self.client.get(f'/api/reviews')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_get_reviews_by_review(self):
        response = self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        review_id = response.json['reviewId']
        response = self.client.get(f'/api/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 6)

    def test_get_reviews_by_book(self):
        self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        response = self.client.get(f'/api/reviews/books/{self.book_id}/reviews')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_update_review(self):
        response = self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        review_id = response.json['reviewId']
        response = self.client.put(f'/api/reviews/{review_id}', json={
            'content': 'Awesome book!',
            'rating': 4,
            'authorization': 'admin'
        })
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json['content'], 'Awesome book!')
        self.assertEqual(response.json['message'], "Review information updated successfully")

    def test_delete_review(self):
        response = self.client.post('/api/reviews', json={
            'user_id': self.user_id,
            'book_id': self.book_id,
            'content': 'Great book!',
            'rating': 5,
            'authorization': "student"
        })
        review_id = response.json['reviewId']
        response = self.client.delete(f'/api/reviews/{review_id}', json={
            'authorization': 'admin'
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
