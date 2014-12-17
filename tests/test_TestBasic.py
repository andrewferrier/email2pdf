from datetime import datetime
from email.message import Message

import os
import tempfile

from tests.BaseTestClasses import BaseTestClasses

class TestBasic(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()
        self.msg = Message()

    def test_dontPrintBody(self):
        self.assertEqual(1, self.invokeEmail2PDF(extraParams=['--no-body'], sysErrExpected=True)[0])
        self.assertFalse(self.existsByTime())

    def test_noheaders(self):
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_simple(self):
        self.addHeaders()
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_simple_withinputfile(self):
        self.addHeaders()
        self.assertEqual(0, self.invokeEmail2PDF(inputFile=True)[0])
        self.assertTrue(self.existsByTime())

    def test_nosubject(self):
        self.addHeaders("from@example.org", "to@example.org", None)
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_plaincontent(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_plaincontent_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "plaincontent_poundsign_iso88591.pdf")
        self.setPlainContent("Hello - this email costs \xa35!", charset="ISO-8859-1")
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))

    def test_plaincontent_metadata(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_metadata.pdf")
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))
        self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
        self.assertEqual("to@example.org", self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual("Subject of the email", self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))

    def test_plaincontent_metadata_differentmount(self):
        self.addHeaders("from@example.org")
        self.setPlainContent("Hello!")
        mountPoint2 = tempfile.mkdtemp(dir='/var/tmp')
        if(self.find_mount_point(mountPoint2) != self.find_mount_point(tempfile.tempdir)):
            path = os.path.join(mountPoint2, "plaincontent_metadata_differentmount.pdf")
            self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
            self.assertTrue(os.path.exists(path))
            self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
        else:
            self.skipTest(mountPoint2 + " and " + tempfile.tempdir + " are on the same mountpoint, test not relevant.")

    def test_noheaders_metadata(self):
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_noheaders_metadata.pdf")
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))
        self.assertIsNone(self.getMetadataField(path, "Author"))
        self.assertIsNone(self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual('', self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))

    def test_plaincontent_headers(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--headers'])[0])
        self.assertTrue(self.existsByTime())

    def test_plaincontent_notrailingslash(self):
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(outputDirectory="/tmp")[0])
        self.assertTrue(self.existsByTime("/tmp"))

    def test_plaincontent_trailingslash(self):
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(outputDirectory="/tmp/")[0])
        self.assertTrue(self.existsByTime("/tmp/"))

    def test_plaincontent_outputfileoverrides(self):
        path = os.path.join(self.examineDir, "outputFileOverrides.pdf")
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(outputDirectory="/tmp", outputFile=path)[0])
        self.assertFalse(self.existsByTime("/tmp"))
        self.assertTrue(os.path.exists(path))

    def test_plaincontent_dirnotexist(self):
        self.setPlainContent("Hello!")
        self.assertEqual(2, self.invokeEmail2PDF(outputDirectory="/notexist/", sysErrExpected=True)[0])

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        try:
            self.assertEqual(2, self.invokeEmail2PDF(outputFile=f_path, sysErrExpected=True)[0])
        finally:
            os.unlink(f_path)

    def test_plaincontent_timedfileexist(self):
        self.setPlainContent("Hello!")
        filename1 = self.getTimeStamp(datetime.now()) + ".pdf"
        filename2 = self.getTimeStamp(datetime.now()) + "_1.pdf"
        self.touch(os.path.join(self.workingDir, filename1))
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(os.path.join(self.workingDir, filename1))
        self.assertTrue(os.path.join(self.workingDir, filename2))

    def test_verbose(self):
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['-v'], sysErrExpected=True)[0])

    def test_veryverbose(self):
        self.setPlainContent("Hello!")
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['-vv'], sysErrExpected=True)[0])
