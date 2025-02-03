import unittest
import testUtils

class TestStudentCode(unittest.TestCase):

    # @message: Tests of de output hello world is
    def test_OutputIsHelloWorld(self):
        output = testUtils.run_student_file("hello_world.py") # Looks in `src` folder for this file
        self.assertRegex(output, "hello world!")


if __name__ == '__main__':
    unittest.main()
