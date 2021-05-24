import unittest


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config_json(self):
        import json
        with open('config/config.json') as fp:
            config = json.load(fp)
        print('300502' in config)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(ConfigTestCase('test_config_json'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())