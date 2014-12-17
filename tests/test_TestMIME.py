from datetime import datetime
from email.mime.multipart import MIMEMultipart

import os

from tests import BaseTestClasses

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
