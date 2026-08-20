import unittest
import json
from app import app, db
from models import User, ScanHistory

class PhishingDetectorTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            test_user = User(email='test@example.com', name='Test User')
            test_user.set_password('Test@123')
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email='test@example.com', password='Test@123'):
        return self.client.post('/', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Phishing Detection System', response.data)

    def test_signup(self):
        response = self.client.post('/signup', data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'NewPass@123',
            'confirm_password': 'NewPass@123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully', response.data)

        with app.app_context():
            user = User.query.filter_by(email='newuser@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'New User')

    def test_login_success(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

    def test_login_failure(self):
        response = self.login(password='WrongPassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_scan_page_anonymous_access(self):
        response = self.client.get('/scan')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Instant Analysis', response.data)

    def test_scan_page_authenticated(self):
        self.login()
        response = self.client.get('/scan')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Instant Analysis', response.data)

    def test_api_scan_authenticated(self):
        self.login()
        response = self.client.post('/api/scan',
            data=json.dumps({'url': 'https://google.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('url', data)
        self.assertIn('ml_prediction', data)

    def test_api_scan_missing_url(self):
        self.login()
        response = self.client.post('/api/scan',
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_dashboard_authenticated(self):
        self.login()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_history_authenticated(self):
        self.login()
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scan History', response.data)

    def test_batch_scan_authenticated(self):
        self.login()
        response = self.client.get('/batch-scan')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Batch Scan', response.data)

    def test_logout(self):
        self.login()
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out successfully', response.data)

    def test_password_hashing(self):
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertTrue(user.check_password('Test@123'))
            self.assertFalse(user.check_password('WrongPassword'))

    def test_scan_history_creation(self):
        self.login()

        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()

            scan = ScanHistory(
                user_id=user.id,
                url='https://example.com',
                cleaned_url='example.com',
                ml_prediction='Safe Website',
                vt_result='Safe',
                vt_malicious=0,
                vt_suspicious=0,
                vt_harmless=50
            )

            db.session.add(scan)
            db.session.commit()

            scans = ScanHistory.query.filter_by(user_id=user.id).all()
            self.assertEqual(len(scans), 1)
            self.assertEqual(scans[0].url, 'https://example.com')

if __name__ == '__main__':
    unittest.main()
