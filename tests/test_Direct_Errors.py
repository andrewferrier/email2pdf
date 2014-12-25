from email.message import Message

import os
import tempfile

from tests import BaseTestClasses


class Direct_Errors(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Errors, self).setUp()
        self.msg = Message()

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        with self.assertRaisesRegex(Exception, "file.*exist"):
            self.invokeDirectly(outputFile=f_path)
        os.unlink(f_path)

    def test_plaincontent_dirnotexist(self):
        self.setPlainContent("Hello!")
        with self.assertRaisesRegex(Exception, "(?i)directory.*not.*exist"):
            self.invokeDirectly(outputDirectory="/notexist/")
