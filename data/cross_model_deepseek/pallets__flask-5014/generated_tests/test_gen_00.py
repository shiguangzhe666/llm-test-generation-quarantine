import unittest
from flask import Flask
from your_blueprint_file import YourBlueprint

class TestYourBlueprint(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.register_blueprint(YourBlueprint)
    
    def test_blueprint_is_registered(self):
        self.assertIn(YourBlueprint.name, self.app.blueprints)
    
    # Add your other tests here.

if __name__ == '__main__':
    unittest.main()