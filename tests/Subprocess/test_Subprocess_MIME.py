from datetime import datetime
from email.mime.multipart import MIMEMultipart

import os
import tempfile

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_nosubject(self):
        self.addHeaders(Email2PDFTestCase.DEFAULT_FROM, Email2PDFTestCase.DEFAULT_TO, None)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_html(self):
        self.addHeaders()
        self.attachHTML("<p>Some basic textual content</p>")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some\sbasic\stextual\scontent")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_attachtext_upsidedown(self):
        self.addHeaders()
        self.attachText("ɯɐɹƃoɹd ɟpdᄅlᴉɐɯǝ ǝɥʇ ɟo ʇsǝʇ ɐ sᴉ sᴉɥʇ ollǝH")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "ɯɐɹƃoɹd\sɟpdᄅlᴉɐɯǝ\sǝɥʇ\sɟo\sʇsǝʇ\sɐ\ssᴉ\ssᴉɥʇ\sollǝH")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_attachhtml_upsidedown(self):
        self.addHeaders()
        self.attachHTML("<p>ɯɐɹƃoɹd ɟpdᄅlᴉɐɯǝ ǝɥʇ ɟo ʇsǝʇ ɐ sᴉ sᴉɥʇ ollǝH</p>")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "ɯɐɹƃoɹd\sɟpdᄅlᴉɐɯǝ\sǝɥʇ\sɟo\sʇsǝʇ\sɐ\ssᴉ\ssᴉɥʇ\sollǝH")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_html_entities_currency(self):
        path = os.path.join(self.examineDir, "htmlEntitiesCurrency.pdf")
        self.addHeaders()
        self.attachHTML(b'<span>Pounds: \xc2\xa37.14, Another Pounds: &#163;7.14</span>'.decode('utf-8'))
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Pounds:\s£7.14,\sAnother\sPounds:\s£7.14")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_html_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "html_poundsign_iso88591.pdf")
        self.attachHTML("Hello - this email costs \xa35!", charset="ISO-8859-1")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Hello\s-\sthis\semail\scosts\s\xa35!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_text_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "text_poundsign_iso88591.pdf")
        self.attachText("Hello - this email costs \xa35!", charset="ISO-8859-1")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Hello\s-\sthis\semail\scosts\s\xa35!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_poundsign_utf8_8bit(self):
        input_email = ("From: \"XYZ\" <xyz@abc.uk>\n"
                       "To: \"XYZ\" <xyz@gmail.com>\n"
                       "Subject: Blah\n"
                       "Content-Type: multipart/mixed; boundary=\"CUT-HERE--\"\n"
                       "\n"
                       "--CUT-HERE--\n"
                       "Content-Type: text/plain; charset=UTF-8\n"
                       "Content-Transfer-Encoding: 8bit\n"
                       "\n"
                       "Price is £45.00\n"
                       "--CUT-HERE----\n")
        path = os.path.join(self.examineDir, "plaincontent_poundsign_utf8_8bit.pdf")
        (rc, output, error) = self.invokeAsSubprocess(inputFile=input_email, outputFile=path,
                                                      extraParams=['--input-encoding=utf-8'])
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Price\sis\s£45.00")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plainandhtml(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachHTML("<p>Some basic HTML content</p>")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some\sbasic\sHTML\scontent")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_pdf(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Some\sbasic\stextual\scontent")
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some\sPDF\scontent")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_outputfileoverrides_with_attachments(self):
        mainFilename = os.path.join(self.examineDir, "outputFileOverridesWithAttachments.pdf")
        self.attachText("Hello!")
        attachmentFilename = self.attachPDF("Some PDF content")
        with tempfile.TemporaryDirectory() as tempdir:
            (rc, output, error) = self.invokeAsSubprocess(outputDirectory=tempdir, outputFile=mainFilename)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertFalse(self.existsByTime())
            self.assertFalse(self.existsByTime(tempdir))
            self.assertFalse(os.path.exists(os.path.join(tempdir, "outputFileOverrides.pdf")))
            self.assertFalse(os.path.exists(os.path.join(self.workingDir, "outputFileOverrides.pdf")))
            self.assertTrue(os.path.exists(mainFilename))
            self.assertFalse(os.path.exists(os.path.join(self.examineDir, attachmentFilename)))
            self.assertFalse(os.path.exists(os.path.join(self.workingDir, attachmentFilename)))
            self.assertTrue(os.path.exists(os.path.join(tempdir, attachmentFilename)))
            self.assertRegex(self.getPDFText(mainFilename), "Hello!")
            self.assertRegex(self.getPDFText(os.path.join(tempdir, attachmentFilename)), "Some\sPDF\scontent")
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())

    def test_remote_image_does_exist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="' + self.EXIST_IMG + '">')
            (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertTrue(os.path.exists(path))
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())
        else:
            self.skipTest("Not online.")

    def test_remote_image_does_exist_uppercase(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesExistUppercase.pdf")
            self.addHeaders()
            self.attachHTML('<img src="' + self.EXIST_IMG_UPPERCASE + '">')
            (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertTrue(os.path.exists(path))
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())
        else:
            self.skipTest("Not online.")

    def test_non_embedded_image_jpeg(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_non_embedded_image_jpeg_add_prefix_date(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--add-prefix-date'])
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, datetime.now().strftime("%Y-%m-%d-") + imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_non_embedded_image_png(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=False)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_non_embedded_image_and_pdf(self):
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
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, filename)), "Some\sPDF\scontent")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
