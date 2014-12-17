#!/usr/bin/env python3

from datetime import datetime
from email.message import Message
from email.mime.multipart import MIMEMultipart

import os
import requests
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


class TestMIME(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(TestMIME, self).setUp()
        self.msg = MIMEMultipart()

    def test_noheaders(self):
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_simple(self):
        self.addHeaders()
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_nosubject(self):
        self.addHeaders("from@example.org", "to@example.org", None)
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_plain(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_plainNoBody(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--no-body'])[0])
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_plainNoAttachments(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        filename2 = self.attachPDF("Some PDF content")
        filename3 = self.attachImage()
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--no-attachments'])[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename3)))

    def test_plainNoBodyNoAttachments(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.attachPDF("Some PDF content")
        self.attachImage()
        self.assertNotEqual(0, self.invokeEmail2PDF(sysErrExpected=True, extraParams=['--no-body', '--no-attachments'])[0])

    def test_html(self):
        self.addHeaders()
        self.attachHTML("<p>Some basic textual content</p>")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_htmlEntitiesCurrency(self):
        path = os.path.join(self.examineDir, "htmlEntitiesCurrency.pdf")
        self.addHeaders()
        self.attachHTML(b'<span>Pounds: \xc2\xa37.14, Another Pounds: &#163;7.14</span>'.decode('utf-8'))
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))

    def test_plainandhtml(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        self.attachHTML("<p>Some basic textual content</p>")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_pdf(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_pdfAsOctetStream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", mainContentType="application", subContentType="octet-stream")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_remoteImageDoesExist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="https://raw.githubusercontent.com/andrewferrier/email2pdf/master/basi2c16.png">')
            self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
            self.assertTrue(os.path.exists(path))
        else:
            self.skipTest("Not online.")

    def test_remoteImageDoesntExist(self):
        if self.isOnline:
            path = os.path.join(self.examineDir, "remoteImageDoesntExist.pdf")
            self.addHeaders()
            self.attachHTML('<img src="http://abc.por/blah.jpg">')
            self.assertEqual(0, self.invokeEmail2PDF(outputFile=path, sysErrExpected=True)[0])
            self.assertTrue(os.path.exists(path))
        else:
            self.skipTest("Not online.")

    def test_remoteImageDoesntExistWithPDF(self):
        if self.isOnline:
            self.addHeaders()
            self.attachHTML('<img src="http://abc.por/blah.jpg">')
            filename = self.attachPDF("Some PDF content")
            self.assertEqual(0, self.invokeEmail2PDF(sysErrExpected=True)[0])
            self.assertTrue(self.existsByTime())
            self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        else:
            self.skipTest("Not online.")

    def test_inlineImageNoBody(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        self.assertNotEqual(0, self.invokeEmail2PDF(extraParams=['--no-body'], sysErrExpected=True)[0])
        self.assertFalse(self.existsByTime())

    def test_inlineImage(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

    def test_inlineImageAndPDF(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        pdfFileName = self.attachPDF("Some PDF content")
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--no-body'])[0])
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, pdfFileName)))

    def test_embeddedImage(self):
        path = os.path.join(self.examineDir, "embeddedImage.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid>')
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embeddedImagePNG(self):
        path = os.path.join(self.examineDir, "embeddedImagePNG.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid', jpeg=False)
        self.attachHTML('<img src=cid:myid>')
        self.assertEqual(0, self.invokeEmail2PDF(outputFile=path)[0])
        self.assertTrue(os.path.exists(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embeddedImageCIDUnderscore(self):
        self.addHeaders()
        imageFilename = self.attachImage('<my_id>')
        self.attachHTML('<img src=cid:my_id>')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embeddedImageExtraHTMLContent(self):
        if self.isOnline:
            self.addHeaders()
            imageFilename = self.attachImage('myid')
            self.attachHTML('<p><img src="https://raw.githubusercontent.com/andrewferrier/email2pdf/master/basi2c16.png">' +
                            '<li></li><img src="cid:myid"></p>')
            self.assertEqual(0, self.invokeEmail2PDF()[0])
            self.assertTrue(self.existsByTime())
            self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        else:
            self.skipTest("Not online.")

    def test_embeddedImageUpperCaseHTMLContent(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embeddedImageNoAttachments(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--no-attachments'])[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embeddedImageAsOctetStream(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid', content_type="application/octet-stream")
        self.attachHTML('<IMG SRC="cid:myid">')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_oneEmbeddedOneNotImage(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        imageFilename2 = self.attachImage()
        self.attachHTML('<IMG SRC="cid:myid">')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename2)))

    def test_nonEmbeddedImageJPEG(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_nonEmbeddedImageJPEGAddPrefixDate(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True)
        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--add-prefix-date'])[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, datetime.now().strftime("%Y-%m-%d-") + imageFilename)))

    def test_nonEmbeddedImageJPEGAsOctetStream(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=True, content_type='application/octet-stream')
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_nonEmbeddedImagePNG(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage(jpeg=False)
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_nonEmbeddedImageAndPDF(self):
        self.addHeaders()
        self.attachText("Hello!")
        imageFilename = self.attachImage()
        filename = self.attachPDF("Some PDF content")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_somethingElseAsOctetStream(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content", fileSuffix="xyz", mainContentType="application",
                                  subContentType="octet-stream")
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))

    def test_2pdfs(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        filename2 = self.attachPDF("Some More PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))

        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))

    def test_pdf_exists(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))

        self.touch(os.path.join(self.workingDir, filename))
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))

        rootName, unused_extension = os.path.splitext(filename)
        uniqueName = rootName + "_1.pdf"

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, uniqueName)))

    def test_2pdfs_oneexists(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        filename2 = self.attachPDF("Some More PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename2)))

        self.touch(os.path.join(self.workingDir, filename))
        self.assertEqual(0, self.invokeEmail2PDF()[0])
        self.assertTrue(self.existsByTime())

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename)))
        rootName, unused_extension = os.path.splitext(filename)
        uniqueName = rootName + "_1.pdf"
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, uniqueName)))

        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))
        rootName2, unused_extension2 = os.path.splitext(filename2)
        uniqueName2 = rootName2 + "_1.pdf"
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, uniqueName2)))

    def test_pdf_adddate(self):
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

        self.assertEqual(0, self.invokeEmail2PDF(extraParams=['--add-prefix-date'])[0])
        self.assertTrue(self.existsByTime())
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename2)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename3)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, filename4)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, datetime.now().strftime("%Y-%m-%d-") + filename)))

if __name__ == '__main__':
    unittest.main()
