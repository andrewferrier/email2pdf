from email.mime.multipart import MIMEMultipart

import os

from tests import BaseTestClasses


class Direct_Arguments(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Arguments, self).setUp()
        self.msg = MIMEMultipart()

    def test_simple(self):
        self.addHeaders()
        error = self.invokeDirectly()
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_dontPrintBody(self):
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*or.*attachments")

    def test_plaincontent_headers(self):
        self.addHeaders()
        self.attachText("Hello!")
        error = self.invokeDirectly(extraParams=['--headers'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        pdfText = self.getPDFText(self.getTimedFilename())
        self.assertRegex(pdfText, "Subject")
        self.assertRegex(pdfText, "From")
        self.assertRegex(pdfText, "To")
        self.assertRegex(pdfText, "Hello")

    def test_plainNoAttachments(self):
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

    def test_plainNoBodyNoAttachments(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.attachPDF("Some PDF content")
        self.attachImage()
        with self.assertRaisesRegex(Exception, "attachments.*not allowed with.*body"):
            self.invokeDirectly(extraParams=['--no-body', '--no-attachments'])
        self.assertFalse(self.existsByTime())
