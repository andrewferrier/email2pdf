from email.mime.multipart import MIMEMultipart

import os

from tests import BaseTestClasses


class AttachmentDetection(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(AttachmentDetection, self).setUp()
        self.msg = MIMEMultipart()

    def test_pdfAsOctetStream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_pdfWithInvalidExtension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", extension="pdf")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_pdfAsOctetStreamWithInvalidExtension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", extension="xyz", mainContentType="application", subContentType="octet-stream")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_pdfAsOctetStreamNoBody(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--no-body'])
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_jpegAsOctetStream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        imageFilename = self.attachImage(jpeg=True, content_type="application/octet-stream")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_jpegWithInvalidExtension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        imageFilename = self.attachImage(jpeg=True, extension="blah")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_jpegAsOctetStreamWithInvalidExtension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        imageFilename = self.attachImage(jpeg=True, content_type="application/octet-stream", extension="xyz")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_unidentifiedFile(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachAttachment("application", "data", "some data in some format", "somefile.xyz")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, "somefile.xyz")))
