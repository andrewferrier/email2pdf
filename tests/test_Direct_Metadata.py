from datetime import datetime
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

    def test_plaincontent_metadata_differentmount(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        mountPoint2 = tempfile.mkdtemp(dir='/var/tmp')
        if(self.find_mount_point(mountPoint2) != self.find_mount_point(tempfile.tempdir)):
            path = os.path.join(mountPoint2, "plaincontent_metadata_differentmount.pdf")
            error = self.invokeDirectly(outputFile=path)
            self.assertEqual('', error)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(Email2PDFTestCase.DEFAULT_FROM, self.getMetadataField(path, "Author"))
            self.assertEqual(Email2PDFTestCase.DEFAULT_TO, self.getMetadataField(path, "X-email2pdf-To"))
            self.assertEqual(Email2PDFTestCase.DEFAULT_SUBJECT, self.getMetadataField(path, "Title"))
            self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        else:
            self.skipTest(mountPoint2 + " and " + tempfile.tempdir + " are on the same mountpoint, test not relevant.")

    def test_noheaders_metadata(self):
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_noheaders_metadata.pdf")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertIsNone(self.getMetadataField(path, "Author"))
        self.assertIsNone(self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual('', self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        self.assertRegex(self.getPDFText(path), "Hello!")
