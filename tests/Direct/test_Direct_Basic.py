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

    def test_internationalised_subject(self):
        path = os.path.join(self.examineDir, "internationalised_subject.pdf")
        self.addHeaders(subject=bytes("Hello!", 'iso-8859-1'), subject_encoding='iso-8859-1')
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)

    def test_internationalised_subject2(self):
        path = os.path.join(self.examineDir, "internationalised_subject_jp.pdf")
        self.addHeaders(subject='=?iso-2022-jp?B?GyRCOiNHLyRiSSwkOiRkJGo/ayQyJGsbKEIhIRskQkcvS3ZBMCRO?=')
        error = self.invokeDirectly(outputFile=path, extraParams=['--headers'])
        self.assertTrue(os.path.exists(path))
        self.assertEqual('', error)
