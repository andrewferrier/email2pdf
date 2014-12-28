from datetime import datetime
from email.mime.multipart import MIMEMultipart

import os

from tests.BaseTestClasses import Email2PDFTestCase


class TestMIME(Email2PDFTestCase):
    def setUp(self):
        super(TestMIME, self).setUp()
        self.msg = MIMEMultipart()

    def test_noheaders(self):
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())

    def test_nosubject(self):
        self.addHeaders(Email2PDFTestCase.DEFAULT_FROM, Email2PDFTestCase.DEFAULT_TO, None)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())

    def test_html(self):
        self.addHeaders()
        self.attachHTML("<p>Some basic textual content</p>")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")

    def test_htmlEntitiesCurrency(self):
        path = os.path.join(self.examineDir, "htmlEntitiesCurrency.pdf")
        self.addHeaders()
        self.attachHTML(b'<span>Pounds: \xc2\xa37.14, Another Pounds: &#163;7.14</span>'.decode('utf-8'))
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Pounds: £7.14, Another Pounds: £7.14")

    def test_plainandhtml(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachHTML("<p>Some basic HTML content</p>")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic HTML content")

    def test_pdf(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")

    def test_remoteImageDoesExist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="' + self.EXIST_IMG + '">')
            (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertTrue(os.path.exists(path))
        else:
            self.skipTest("Not online.")

    def test_nonEmbeddedImageJPEG(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")

    def test_nonEmbeddedImageJPEGAddPrefixDate(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--add-prefix-date'])
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, datetime.now().strftime("%Y-%m-%d-") + imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")

    def test_nonEmbeddedImagePNG(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=False)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")

    def test_nonEmbeddedImageAndPDF(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage()
        filename = self.attachPDF("Some PDF content")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")

    def test_2pdfs(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        filename2 = self.attachPDF("Some More PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some PDF content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename2)), "Some More PDF content")

    def test_pdf_exists(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))

        self.touch(os.path.join(self.workingDir, filename))
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

        rootName, unused_extension = os.path.splitext(filename)
        uniqueName = rootName + "_1.pdf"

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, uniqueName)))

        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertIsNone(self.getPDFText(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, uniqueName)), "Some PDF content")

    def test_2pdfs_oneexists(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        filename2 = self.attachPDF("Some More PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))

        self.touch(os.path.join(self.workingDir, filename))
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        rootName, unused_extension = os.path.splitext(filename)
        uniqueName = rootName + "_1.pdf"
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, uniqueName)))

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))
        rootName2, unused_extension2 = os.path.splitext(filename2)
        uniqueName2 = rootName2 + "_1.pdf"
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, uniqueName2)))

        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some basic textual content")
        self.assertIsNone(self.getPDFText(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, uniqueName)), "Some PDF content")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename2)), "Some More PDF content")
