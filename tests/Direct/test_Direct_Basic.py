from email.header import Header
from email.mime.multipart import MIMEMultipart

import os

from tests import BaseTestClasses


class Direct_Basic(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Basic, self).setUp()
        self.msg = MIMEMultipart()

    def test_simple(self):
        self.addHeaders()
        error = self.invokeDirectly()
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_missing_from_to(self):
        path = os.path.join(self.examineDir, "missing_from_to.pdf")
        self.addHeaders(frm=None, to=None)
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_internationalised_subject(self):
        path = os.path.join(self.examineDir, "internationalised_subject.pdf")
        self.addHeaders(subject=bytes("Hello!", 'iso-8859-1'), subject_encoding='iso-8859-1')
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_internationalised_subject2(self):
        path = os.path.join(self.examineDir, "internationalised_subject_jp.pdf")
        self.addHeaders(subject='=?iso-2022-jp?B?GyRCOiNHLyRiSSwkOiRkJGo/ayQyJGsbKEIhIRskQkcvS3ZBMCRO?=')
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_internationalised_subject3(self):
        path = os.path.join(self.examineDir, "internationalised_subject_de.pdf")
        self.addHeaders(subject='Ihre Anfrage, Giesestra=?utf-8?B?w58=?=e 5')
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_internationalised_subject4(self):
        path = os.path.join(self.examineDir, "internationalised_subject_complex.pdf")
        header = Header()
        header.append(bytes('£100', 'iso-8859-1'), 'iso-8859-1')
        header.append(bytes(' is != how much ', 'utf-8'), 'utf-8')
        header.append(bytes('I have to spend!', 'iso-8859-15'), 'iso-8859-15')
        self.addHeaders(subject=header.encode())
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_contains_left_angle_bracket_mime(self):
        path = os.path.join(self.examineDir, "left_angle_bracket_mime.pdf")
        self.attachText("<angle bracket test>")
        error = self.invokeDirectly(outputFile=path)
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(path), "<angle bracket test>")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
