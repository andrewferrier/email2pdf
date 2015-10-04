from email.message import Message

import os

from tests.BaseTestClasses import Email2PDFTestCase


class Direct_BasicPlain(Email2PDFTestCase):
    def setUp(self):
        super(Direct_BasicPlain, self).setUp()
        self.msg = Message()

    def test_contains_left_angle_bracket(self):
        path = os.path.join(self.examineDir, "left_angle_bracket_plain.pdf")
        self.setPlainContent("<angle bracket test>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(path), "<angle bracket test>")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
