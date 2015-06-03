from email.mime.multipart import MIMEMultipart

import os

from tests.BaseTestClasses import Email2PDFTestCase


class Direct_CID(Email2PDFTestCase):
    def setUp(self):
        super(Direct_CID, self).setUp()
        self.msg = MIMEMultipart()

    def test_inline_image_no_body(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*or.*attachments")

    def test_inline_image_and_pdf(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        pdfFileName = self.attachPDF("Some PDF content")
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, pdfFileName)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, pdfFileName)), "Some PDF content")

    def test_embedded_image(self):
        path = os.path.join(self.examineDir, "embeddedImage.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_with_complex_name(self):
        path = os.path.join(self.examineDir, "embeddedImage.png")
        self.addHeaders()
        imageFilename = self.attachImage('myid@A34A.1A23E', jpeg=False)
        self.attachHTML('<img src=cid:myid@A34A.1A23E>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_invalid_cid(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid2>')
        error = self.invokeDirectly()
        self.assertRegex(error, "(?i)could not find image")
        self.assertTrue(self.existsByTime())
        self.assertGreater(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_png(self):
        path = os.path.join(self.examineDir, "embeddedImagePNG.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid', jpeg=False)
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_cid_underscore(self):
        self.addHeaders()
        imageFilename = self.attachImage('<my_id>')
        self.attachHTML('<img src=cid:my_id>')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_extra_html_content(self):
        if self.isOnline:
            self.addHeaders()
            imageFilename = self.attachImage('myid')
            self.attachHTML('<p><img src="' + self.EXIST_IMG + '">' +
                            '<li></li><img src="cid:myid"></p>')
            error = self.invokeDirectly()
            self.assertEqual('', error)
            self.assertTrue(self.existsByTime())
            self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
            self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        else:
            self.skipTest("Not online.")

    def test_embedded_image_upper_case_html_content(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_no_attachments(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly(extraParams=['--no-attachments'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_embedded_image_as_octet_stream(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid', content_type="application/octet-stream")
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_one_embedded_one_not_image(self):
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        imageFilename2 = self.attachImage()
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, imageFilename2)))

    def test_two_embedded(self):
        path = os.path.join(self.examineDir, "twoEmbeddedImages.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid"><IMG SRC="cid:myid">')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))

    def test_two_different_embedded(self):
        path = os.path.join(self.examineDir, "twoDifferentEmbeddedImages.pdf")
        self.addHeaders()
        imageFilename = self.attachImage('myid')
        imageFilename2 = self.attachImage('myid2', jpeg=False)
        self.attachHTML('<IMG SRC="cid:myid"><IMG SRC="cid:myid2">')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE + Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, imageFilename2)))

    def test_some_cids_not_referenced(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachImage('myid2', inline=True)
        self.attachImage('myid3', inline=True)
        self.attachImage(inline=True)
        self.attachImage(inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'myid2.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'myid3.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment.jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment_1.jpg')))

    def test_some_cids_not_referenced_ignore_floating_attachments(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachImage('myid2', inline=True)
        self.attachImage('myid3', inline=True)
        self.attachImage(inline=True)
        self.attachImage(inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly(extraParams=['--ignore-floating-attachments'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.jpg')))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid2.jpg')))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid3.jpg')))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'floating_attachment.jpg')))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'floating_attachment_1.jpg')))

    def test_some_cids_not_referenced_png(self):
        self.addHeaders()
        self.attachImage('myid', jpeg=False, inline=True)
        self.attachImage('myid2', jpeg=False, inline=True)
        self.attachImage(jpeg=False, inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.png')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'myid2.png')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment.png')))

    def test_some_cids_not_referenced_pdf(self):
        self.addHeaders()
        self.attachPDF('Some PDF content', no_filename=True)
        self.attachImage('myid', inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.png')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment.pdf')))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, 'floating_attachment.pdf')), "Some PDF content")

    def test_some_cids_not_referenced_docx(self):
        self.addHeaders()
        self.attachAttachment('application',
                              'vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'Word document content', None)
        self.attachImage('myid', inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.png')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment.docx')))

    def test_some_cids_not_referenced_misc(self):
        self.addHeaders()
        self.attachAttachment('application',
                              'some-random-format',
                              'Document content', None)
        self.attachImage('myid', inline=True)
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.png')))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, 'floating_attachment')))
