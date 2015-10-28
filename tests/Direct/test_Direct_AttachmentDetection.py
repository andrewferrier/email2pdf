from email.mime.multipart import MIMEMultipart

import os

from tests.BaseTestClasses import Email2PDFTestCase


class AttachmentDetection(Email2PDFTestCase):
    def setUp(self):
        super(AttachmentDetection, self).setUp()
        self.msg = MIMEMultipart()

    def test_pdf_as_octet_stream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_pdf_with_invalid_extension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", extension="pdf")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_pdf_as_octet_stream_with_invalid_extension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", extension="xyz", mainContentType="application", subContentType="octet-stream")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_pdf_as_octet_stream_no_body(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_jpeg_as_octet_stream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        image_filename = self.attachImage(jpeg=True, content_type="application/octet-stream")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertIsJPG(os.path.join(self.workingDir, image_filename))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_jpeg_with_invalid_extension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        image_filename = self.attachImage(jpeg=True, extension="blah")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertIsJPG(os.path.join(self.workingDir, image_filename))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_jpeg_as_octet_stream_with_invalid_extension(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        image_filename = self.attachImage(jpeg=True, content_type="application/octet-stream", extension="xyz")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertIsJPG(os.path.join(self.workingDir, image_filename))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_word_document(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachAttachment("application", "vnd.openxmlformats-officedocument.wordprocessingml.document",
                              "Word document content", "somefile.docx")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, "somefile.docx")))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_unidentified_file(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachAttachment("application", "data", "some data in some format", "somefile.xyz")
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, "somefile.xyz")))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_attachment_filename_has_encoding(self):
        path = os.path.join(self.workingDir, "somefile.xyz")
        self.attachAttachment("application", "data", "some data in some format", "somefile.xyz", file_name_encoding="utf-8")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--no-body'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
