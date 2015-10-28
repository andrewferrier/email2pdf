from datetime import datetime
from email.mime.multipart import MIMEMultipart

import os

from tests import BaseTestClasses


class Direct_Arguments(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Arguments, self).setUp()
        self.msg = MIMEMultipart()

    def test_no_body(self):
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*any.*attachments")
        self.assertTrue(self.existsByTimeWarning())
        self.assertTrue(self.existsByTimeOriginal())
        self.assertRegex(self.getWarningFileContents(), "body.*any.*attachments")
        self.assertValidOriginalFileContents()

    def test_no_body_but_some_attachments(self):
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.invokeDirectly(extraParams=['--no-body'])
        self.assertFalse(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")

    def test_no_body_mostly_hide_warnings(self):
        error = self.invokeDirectly(extraParams=['--no-body', '--mostly-hide-warnings'])
        self.assertFalse(self.existsByTime())
        self.assertEqual("", error)
        self.assertTrue(self.existsByTimeWarning())
        self.assertTrue(self.existsByTimeOriginal())
        self.assertRegex(self.getWarningFileContents(), "body.*any.*attachments")
        self.assertValidOriginalFileContents()

    def test_no_attachments(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        filename2 = self.attachPDF("Some PDF content")
        filename3 = self.attachImage()
        error = self.invokeDirectly(extraParams=['--no-attachments'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename3)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_no_attachments_mostly_hide_warnings(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        filename2 = self.attachPDF("Some PDF content")
        filename3 = self.attachImage()
        error = self.invokeDirectly(extraParams=['--no-attachments', '--mostly-hide-warnings'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename3)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_no_body_and_no_attachments(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.attachPDF("Some PDF content")
        self.attachImage()
        with self.assertRaisesRegex(Exception, "attachments.*not allowed with.*body"):
            self.invokeDirectly(extraParams=['--no-body', '--no-attachments'])
        self.assertFalse(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_verbose_and_mostly_hide_warnings(self):
        with self.assertRaisesRegex(Exception, "mostly-hide.*not allowed with.*verbose"):
            self.invokeDirectly(extraParams=['--verbose', '--mostly-hide-warnings'])
        self.assertFalse(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_headers(self):
        path = os.path.join(self.examineDir, "headers.pdf")
        self.addHeaders()
        self.attachText("Hello!")
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        pdf_text = self.getPDFText(path)
        self.assertRegex(pdf_text, "Subject")
        self.assertRegex(pdf_text, "From")
        self.assertRegex(pdf_text, "To")
        self.assertRegex(pdf_text, "Hello")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_add_prefix_date(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        filename2 = self.attachPDF("Some PDF content", filePrefix="unittest_file_2014-01-01")
        filename3 = self.attachPDF("Some PDF content", filePrefix="unittest_2014-01-01_file")
        filename4 = self.attachPDF("Some PDF content", filePrefix="2014-01-01_unittest_file")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename3)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename4)))
        error = self.invokeDirectly(extraParams=['--add-prefix-date'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename3)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename4)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, datetime.now().strftime("%Y-%m-%d-") + filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename2)), "Some PDF content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename3)), "Some PDF content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename4)), "Some PDF content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir,
                                                      datetime.now().strftime("%Y-%m-%d-") + filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_verbose(self):
        self.attachText("Hello!")
        error = self.invokeDirectly(extraParams=['-v'])
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_veryverbose(self):
        self.attachText("Hello!")
        error = self.invokeDirectly(extraParams=['-vv'])
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
