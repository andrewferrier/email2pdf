from email.message import Message

import os
import tempfile

from tests import BaseTestClasses


class TestBasic(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()
        self.msg = Message()

    def test_dontPrintBody(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--no-body'])
        self.assertEqual(1, rc)
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*or.*attachments")

    def test_noheaders(self):
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_withinputfile(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess(inputFile=True)
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_withinputfile_metadata(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess(inputFile=True)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        timedFilename = self.getTimedFilename()
        self.assertTrue(os.path.exists(timedFilename))
        self.assertEqual("from@example.org", self.getMetadataField(timedFilename, "Author"))

    def test_nosubject(self):
        self.addHeaders("from@example.org", "to@example.org", None)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_plaincontent(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")

    def test_plaincontent_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "plaincontent_poundsign_iso88591.pdf")
        self.setPlainContent("Hello - this email costs \xa35!", charset="ISO-8859-1")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Hello - this email costs \xa35!")

    def test_plaincontent_metadata(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_metadata.pdf")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
        self.assertEqual("to@example.org", self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual("Subject of the email", self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        self.assertRegex(self.getPDFText(path), "Hello!")

    def test_plaincontent_metadata_differentmount(self):
        self.addHeaders("from@example.org")
        self.setPlainContent("Hello!")
        mountPoint2 = tempfile.mkdtemp(dir='/var/tmp')
        if(self.find_mount_point(mountPoint2) != self.find_mount_point(tempfile.tempdir)):
            path = os.path.join(mountPoint2, "plaincontent_metadata_differentmount.pdf")
            (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertTrue(os.path.exists(path))
            self.assertEqual("from@example.org", self.getMetadataField(path, "Author"))
            self.assertRegex(self.getPDFText(path), "Hello!")
        else:
            self.skipTest(mountPoint2 + " and " + tempfile.tempdir + " are on the same mountpoint, test not relevant.")

    def test_noheaders_metadata(self):
        self.setPlainContent("Hello!")
        path = os.path.join(self.examineDir, "plaincontent_noheaders_metadata.pdf")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertIsNone(self.getMetadataField(path, "Author"))
        self.assertIsNone(self.getMetadataField(path, "X-email2pdf-To"))
        self.assertEqual('', self.getMetadataField(path, "Title"))
        self.assertEqual("email2pdf", self.getMetadataField(path, "Producer"))
        self.assertRegex(self.getPDFText(path), "Hello!")

    def test_plaincontent_notrailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(outputDirectory="/tmp")
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime("/tmp"))
        self.assertRegex(self.getPDFText(self.getTimedFilename("/tmp/")), "Hello!")

    def test_plaincontent_trailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(outputDirectory="/tmp")
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime("/tmp/"))
        self.assertRegex(self.getPDFText(self.getTimedFilename("/tmp/")), "Hello!")

    def test_plaincontent_outputfileoverrides(self):
        filename = os.path.join(self.examineDir, "outputFileOverrides.pdf")
        pathname = tempfile.mkdtemp(dir='/tmp')
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(outputDirectory=pathname, outputFile=filename)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime(pathname))
        self.assertTrue(os.path.exists(filename))
        self.assertRegex(self.getPDFText(filename), "Hello!")

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        try:
            (rc, output, error) = self.invokeAsSubprocess(outputFile=f_path)
            self.assertEqual(2, rc)
            self.assertRegex(error, "file.*exist")
        finally:
            os.unlink(f_path)

    def test_verbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['-v'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")

    def test_veryverbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['-vv'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
