from email.mime.multipart import MIMEMultipart

import os
import tempfile

from tests import BaseTestClasses


class Direct_Errors(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Errors, self).setUp()
        self.msg = MIMEMultipart()

    def test_plaincontent_fileexist(self):
        self.attachText("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        with self.assertRaisesRegex(Exception, "file.*exist"):
            self.invokeDirectly(outputFile=f_path)
        os.unlink(f_path)

    def test_plaincontent_dirnotexist(self):
        self.attachText("Hello!")
        with self.assertRaisesRegex(Exception, "(?i)directory.*not.*exist"):
            self.invokeDirectly(outputDirectory="/notexist/")

    def test_image_doesnt_exist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesntExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="' + self.NONEXIST_IMG + '">')
            error = self.invokeDirectly(outputFile=path)
            self.assertTrue(os.path.exists(path))
            self.assertRegex(error, "(?i)could not retrieve")
        else:
            self.skipTest("Not online.")

    def test_image_doesnt_exist_with_pdf(self):
        if self.isOnline:
            self.addHeaders()
            self.attachHTML('<img src="' + self.NONEXIST_IMG + '">')
            filename = self.attachPDF("Some PDF content")
            error = self.invokeDirectly()
            self.assertTrue(self.existsByTime())
            self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
            self.assertRegex(error, "(?i)could not retrieve")
        else:
            self.skipTest("Not online.")
