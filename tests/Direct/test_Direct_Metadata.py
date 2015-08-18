from email.message import Message

import os
import tempfile

from tests.BaseTestClasses import Email2PDFTestCase


class Direct_Metadata(Email2PDFTestCase):
    def setUp(self):
        super(Direct_Metadata, self).setUp()
        self.msg = Message()

    def test_metadata(self):
        self.addHeaders()
        error = self.invokeDirectly()
        self.assertEqual('', error)
        timedFilename = self.getTimedFilename()
        self.assertTrue(os.path.exists(timedFilename))
        self.assertEqual(Email2PDFTestCase.DEFAULT_FROM, self.getMetadataField(timedFilename, "Author"))
        self.assertEqual(Email2PDFTestCase.DEFAULT_TO, self.getMetadataField(timedFilename, "X-email2pdf-To"))
        self.assertEqual(Email2PDFTestCase.DEFAULT_SUBJECT, self.getMetadataField(timedFilename, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(timedFilename, "Producer"))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_metadata(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_metadata.pdf")
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(Email2PDFTestCase.DEFAULT_FROM, self.getMetadataField(path, "Author"))
        self.assertEqual(Email2PDFTestCase.DEFAULT_TO, self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual(Email2PDFTestCase.DEFAULT_SUBJECT, self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        self.assertRegex(self.getPDFText(path), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_metadata_differentmount(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        with tempfile.TemporaryDirectory(dir='/var/tmp') as tempdir:
            if(self.find_mount_point(tempdir) != self.find_mount_point(tempfile.tempdir)):
                path = os.path.join(tempdir, "plaincontent_metadata_differentmount.pdf")
                error = self.invokeDirectly(outputFile=path)
                self.assertEqual('', error)
                self.assertTrue(os.path.exists(path))
                self.assertEqual(Email2PDFTestCase.DEFAULT_FROM, self.getMetadataField(path, "Author"))
                self.assertEqual(Email2PDFTestCase.DEFAULT_TO, self.getMetadataField(path, "X-email2pdf-To"))
                self.assertEqual(Email2PDFTestCase.DEFAULT_SUBJECT, self.getMetadataField(path, "Title"))
                self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
                self.assertFalse(self.existsByTimeWarning())
                self.assertFalse(self.existsByTimeOriginal())
            else:
                self.skipTest(tempdir + " and " + tempfile.tempdir + " are on the same mountpoint, test not relevant.")

    def test_noheaders_metadata(self):
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_noheaders_metadata.pdf")
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertIsNone(self.getMetadataField(path, "Author"))
        self.assertIsNone(self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual('', self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        self.assertRegex(self.getPDFText(path), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_metadata_internationalised_subject(self):
        self.addHeaders(subject=bytes("Hello!", 'iso-8859-1'), subject_encoding='iso-8859-1')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        timedFilename = self.getTimedFilename()
        self.assertTrue(os.path.exists(timedFilename))
        self.assertEqual(Email2PDFTestCase.DEFAULT_FROM, self.getMetadataField(timedFilename, "Author"))
        self.assertEqual(Email2PDFTestCase.DEFAULT_TO, self.getMetadataField(timedFilename, "X-email2pdf-To"))
        self.assertEqual("Hello!", self.getMetadataField(timedFilename, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(timedFilename, "Producer"))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
