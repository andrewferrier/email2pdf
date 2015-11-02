from email.mime.multipart import MIMEMultipart

import os
import tempfile
import unittest.mock

from tests import BaseTestClasses


class Direct_Errors(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Errors, self).setUp()
        self.msg = MIMEMultipart()

    def test_plaincontent_fileexist(self):
        self.attachText("Hello!")
        with tempfile.NamedTemporaryFile() as tmpfile:
            with self.assertRaisesRegex(Exception, "file.*exist"):
                self.invokeDirectly(outputFile=tmpfile.name, okToExist=True)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_dirnotexist(self):
        self.attachText("Hello!")
        with self.assertRaisesRegex(Exception, "(?i)directory.*not.*exist"):
            self.invokeDirectly(outputDirectory="/notexist/")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_image_doesnt_exist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesntExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="' + self.NONEXIST_IMG + '">')
            error = self.invokeDirectly(outputFile=path)
            self.assertTrue(os.path.exists(path))
            self.assertRegex(error, "(?i)could not retrieve")
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())
        else:
            self.skipTest("Not online.")

    def test_image_doesnt_exist_blacklist(self):
        path = os.path.join(self.examineDir, "remoteImageDoesntExistBlacklist.pdf")
        self.addHeaders()
        self.attachHTML('<img src="' + self.NONEXIST_IMG_BLACKLIST + '">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_image_doesnt_exist_blacklist_upper(self):
        path = os.path.join(self.examineDir, "remoteImageDoesntExistBlacklistUpper.pdf")
        self.addHeaders()
        self.attachHTML('<img src="' + self.NONEXIST_IMG_BLACKLIST.upper() + '">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_image_doesnt_exist_with_pdf(self):
        if self.isOnline:
            self.addHeaders()
            self.attachHTML('<img src="' + self.NONEXIST_IMG + '">')
            filename = self.attachPDF("Some PDF content")
            error = self.invokeDirectly()
            self.assertTrue(self.existsByTime())
            self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
            self.assertRegex(error, "(?i)could not retrieve")
            self.assertTrue(self.existsByTimeWarning())
            self.assertRegex(self.getWarningFileContents(), "(?i)could not retrieve")
            self.assertTrue(self.existsByTimeOriginal())
            self.assertValidOriginalFileContents()
        else:
            self.skipTest("Not online.")

    def test_local_image_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localImageDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML('<img src="/test.png">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(error, "(?i)could not retrieve")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_local_image_with_query_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localImageWithQueryDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML('<img src="/test.png?foo=bar">')
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(error, "(?i)could not retrieve")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_local_script_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localScriptDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML("<script src=\"/test.js\"></script>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_local_script_with_query_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localScriptWithQueryDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML("<script src=\"/test.js?muh\"></script>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_local_stylesheet_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localStylesheetDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML("<html><head><link href=\"/test.css\" rel=\"stylesheet\"></head></html>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_local_stylesheet_with_query_doesnt_exist(self):
        path = os.path.join(self.examineDir, "localStylesheetWithQueryDoesntExist.pdf")
        self.addHeaders()
        self.attachHTML("<html><head><link href=\"/test.css?muh\" rel=\"stylesheet\"></head></html>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_no_explicit_parts(self):
        # If we don't add any parts explicitly, email2pdf should find a
        # plain-text part
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_fuzz(self):
        with self.assertRaisesRegex(Exception, "(?i)defects parsing email"):
            self.invokeDirectly(completeMessage="This is total junk")
        self.assertFalse(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_broken_html(self):
        self.addHeaders()
        self.attachHTML('<img<a<h href')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_missing_wkhtmltopdf(self):
        with unittest.mock.patch.dict(os.environ, {'PATH': ''}):
            with self.assertRaisesRegex(Exception, "(?i)email2pdf requires wkhtmltopdf"):
                self.invokeDirectly()
            self.assertFalse(self.existsByTime())
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())
