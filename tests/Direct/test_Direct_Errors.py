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
        with tempfile.NamedTemporaryFile() as tmpfile:
            with self.assertRaisesRegex(Exception, "file.*exist"):
                self.invokeDirectly(outputFile=tmpfile.name)

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

    def test_image_doesnt_exist_blacklist(self):
        path = os.path.join(self.examineDir, "remoteImageDoesntExistBlacklist.pdf")
        self.addHeaders()
        self.attachHTML('<img src="' + self.NONEXIST_IMG_BLACKLIST + '">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)

    def test_image_doesnt_exist_blacklist(self):
        path = os.path.join(self.examineDir, "remoteImageDoesntExistBlacklistUpper.pdf")
        self.addHeaders()
        self.attachHTML('<img src="' + self.NONEXIST_IMG_BLACKLIST.upper() + '">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)

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

    def test_no_explicit_parts(self):
        # If we don't add any parts explicitly, email2pdf should find a
        # plain-text part
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())

    def test_fuzz(self):
        with self.assertRaisesRegex(Exception, "(?i)defects parsing email"):
            error = self.invokeDirectly(completeMessage="This is total junk")
        self.assertFalse(self.existsByTime())

    def test_broken_html(self):
        self.addHeaders()
        self.attachHTML('<img<a<h href')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
