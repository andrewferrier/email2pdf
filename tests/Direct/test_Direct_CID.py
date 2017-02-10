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
        self.assertRegex(error, "body.*any.*attachments")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, 'myid.jpg')))
        self.assertTrue(self.existsByTimeWarning())
        self.assertRegex(self.getWarningFileContents(), "body.*any.*attachments")
        self.assertTrue(self.existsByTimeOriginal())
        self.assertValidOriginalFileContents()

    def test_inline_image_with_filename_no_body(self):
        self.addHeaders()
        image_filename = self.attachImage('myid', inline=True, force_filename=True)
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_inline_image_and_pdf(self):
        self.addHeaders()
        self.attachImage('myid', inline=True)
        self.attachHTML('<img src=cid:myid>')
        pdf_file_name = self.attachPDF("Some PDF content")
        error = self.invokeDirectly(extraParams=['--no-body'])
        self.assertEqual('', error)
        self.assertFalse(self.existsByTime())
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, pdf_file_name)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, pdf_file_name)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image(self):
        path = os.path.join(self.examineDir, "embeddedImage.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    # This test is an attempt to recreate a real-world failing email where the image attachment looked like:
    #
    # Content-Type: image/png; name=map_8dff3523-1a2d-4fc8-926f-d18e93964f3d
    # Content-Disposition: inline; filename=map_8dff3523-1a2d-4fc8-926f-d18e93964f3d
    # Content-Transfer-Encoding: base64
    # Content-ID: <>
    #
    # And the HTML looked like:
    #
    # <img src="cid:map_8dff3523-1a2d-4fc8-926f-d18e93964f3d">

    def test_embedded_image_cid_empty(self):
        path = os.path.join(self.examineDir, "embeddedImageCIDEmpty.pdf")
        self.addHeaders()
        image_filename = self.attachImage('<>', jpeg=False, inline=True, force_filename=True, content_type_add_filename=True, extension="")
        self.attachHTML('<img src=cid:' + image_filename + '>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_with_complex_name(self):
        path = os.path.join(self.examineDir, "embeddedImageWithComplexName.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid@A34A.1A23E', jpeg=False)
        self.attachHTML('<img src=cid:myid@A34A.1A23E>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_invalid_cid(self):
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid2>')
        error = self.invokeDirectly()
        self.assertRegex(error, "(?i)could not find image")
        self.assertTrue(self.existsByTime())
        self.assertGreater(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertTrue(self.existsByTimeWarning())
        self.assertRegex(self.getWarningFileContents(), "(?i)could not find image")
        self.assertTrue(self.existsByTimeOriginal())
        self.assertValidOriginalFileContents()

    def test_embedded_image_invalid_cid_output_file(self):
        path = os.path.join(self.workingDir, "test_embedded_image_invalid_cid_output_file.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<img src=cid:myid2>')
        error = self.invokeDirectly(outputFile=path)
        self.assertRegex(error, "(?i)could not find image")
        self.assertTrue(os.path.exists(path))
        self.assertGreater(Email2PDFTestCase.JPG_SIZE, os.path.getsize(path))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename)))
        warning_filename = os.path.join(self.workingDir, "test_embedded_image_invalid_cid_output_file_warnings_and_errors.txt")
        self.assertTrue(os.path.exists(warning_filename))
        with open(warning_filename) as f:
            warning_file_contents = f.read()
        self.assertRegex(warning_file_contents, "(?i)could not find image")
        original_email_filename = os.path.join(self.workingDir, "test_embedded_image_invalid_cid_output_file_original.eml")
        self.assertTrue(os.path.exists(original_email_filename))
        self.assertValidOriginalFileContents(filename=original_email_filename)

    def test_embedded_image_png(self):
        path = os.path.join(self.examineDir, "embeddedImagePNG.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid', jpeg=False)
        self.attachHTML('<img src=cid:myid>')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_cid_underscore(self):
        self.addHeaders()
        image_filename = self.attachImage('<my_id>')
        self.attachHTML('<img src=cid:my_id>')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_extra_html_content(self):
        if self.isOnline:
            self.addHeaders()
            image_filename = self.attachImage('myid')
            self.attachHTML('<p><img src="' + self.EXIST_IMG + '">' +
                            '<li></li><img src="cid:myid"></p>')
            error = self.invokeDirectly()
            self.assertEqual('', error)
            self.assertTrue(self.existsByTime())
            self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
            self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())
        else:
            self.skipTest("Not online.")

    def test_embedded_image_upper_case_html_content(self):
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_no_attachments(self):
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly(extraParams=['--no-attachments'])
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_embedded_image_as_octet_stream(self):
        self.addHeaders()
        image_filename = self.attachImage('myid', content_type="application/octet-stream")
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_one_embedded_one_not_image(self):
        self.addHeaders()
        image_filename = self.attachImage('myid')
        image_filename2 = self.attachImage()
        self.attachHTML('<IMG SRC="cid:myid">')
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(self.getTimedFilename()))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, image_filename2)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_two_embedded(self):
        path = os.path.join(self.examineDir, "twoEmbeddedImages.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid')
        self.attachHTML('<IMG SRC="cid:myid"><IMG SRC="cid:myid">')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_two_different_embedded(self):
        path = os.path.join(self.examineDir, "twoDifferentEmbeddedImages.pdf")
        self.addHeaders()
        image_filename = self.attachImage('myid')
        image_filename2 = self.attachImage('myid2', jpeg=False)
        self.attachHTML('<IMG SRC="cid:myid"><IMG SRC="cid:myid2">')
        error = self.invokeDirectly(outputFile=path)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertLess(Email2PDFTestCase.JPG_SIZE + Email2PDFTestCase.PNG_SIZE, os.path.getsize(path))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename)))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, image_filename2)))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

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
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
