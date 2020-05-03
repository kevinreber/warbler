"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        uid1 = 1111
        u1 = User.signup("test1", "test1@test.com", "password", None)
        u1.id = uid1

        uid2 = 2222
        u2 = User.signup("test2", "test2@test.com", "password", None)
        u2.id = uid2

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1 = User.query.get(uid1)
        self.u2 = User.query.get(uid2)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    ####
    #
    # Following tests
    #
    ####
    def test_user_follows(self):
        """Tests if users can follow each other"""
        self.u1.following.append(self.u2)
        db.session.commit()

        # test followers
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)

        # test following
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)

        # test followers id
        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    ####
    #
    # Signup tests
    #
    ####

    ####
    #
    # Authentication tests
    #
    ####
    def test_valid_authentication(self):
        """User data should be returned if User.authenticate"""
        user = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1.id)

    def test_invalid_username(self):
        """Should return False if incorrect username"""
        self.assertFalse(User.authenticate("wrong_username", "password"))

    def test_wrong_password(self):
        """Should return False if incorrect password"""
        self.assertFalse(User.authenticate(self.u1.username, "wrong_password"))
