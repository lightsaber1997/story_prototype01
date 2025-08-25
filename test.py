import unittest
from format_helper import single_key_bool_json_fix  


class TestSingleKeyBoolJsonFix(unittest.TestCase):

    def test_correct_json(self):
        self.assertEqual(single_key_bool_json_fix('{"is_story":"true"}'),
                         {"is_story": "true"})
        self.assertEqual(single_key_bool_json_fix('{"is_story":"false"}'),
                         {"is_story": "false"})

    def test_missing_quotes_around_key(self):
        self.assertEqual(single_key_bool_json_fix('{is_story:"true"}'),
                         {"is_story": "true"})
        self.assertEqual(single_key_bool_json_fix('{is_story:"false"}'),
                         {"is_story": "false"})

    def test_boolean_literals(self):
        self.assertEqual(single_key_bool_json_fix('{is_story:true}'),
                         {"is_story": "true"})
        self.assertEqual(single_key_bool_json_fix('{is_story:false}'),
                         {"is_story": "false"})
        self.assertEqual(single_key_bool_json_fix('{"is_story":true}'),
                         {"is_story": "true"})
        self.assertEqual(single_key_bool_json_fix('{"is_story":false}'),
                         {"is_story": "false"})

    def test_extra_whitespace(self):
        self.assertEqual(single_key_bool_json_fix('{   is_story   :   true   }'),
                         {"is_story": "true"})

    def test_wrong_field(self):
        # If key doesn't match "is_story", it should still parse normally
        self.assertEqual(single_key_bool_json_fix('{fixed_line:"Hello"}', field="fixed_line"),
                         {"fixed_line": "Hello"})

    def test_non_json_text(self):
        self.assertEqual(single_key_bool_json_fix("hello world"), {})

    def test_invalid_json(self):
        self.assertEqual(single_key_bool_json_fix("{is_story:"), {})


if __name__ == "__main__":
    unittest.main()
