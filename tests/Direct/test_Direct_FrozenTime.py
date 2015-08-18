from datetime import datetime
from email.mime.multipart import MIMEMultipart
from freezegun import freeze_time

import os

from tests import BaseTestClasses


class Direct_Complex(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Complex, self).setUp()
        self.msg = MIMEMultipart()

    @freeze_time("2016-08-09 23:04:05")
    def test_simple(self):
        self.addHeaders()
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, "2016-08-09T23-04-05.pdf")))
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    @freeze_time("2017-09-11 00:05:06")
    def test_add_prefix_date(self):
        self.addHeaders()
        self.attachText("Some basic textual content")
        filename = self.attachPDF("Some PDF content")
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        error = self.invokeDirectly(extraParams=['--add-prefix-date'])
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, "2017-09-11T00-05-06.pdf")))
        self.assertFalse(os.path.exists(os.path.join(self.workingDir, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.workingDir, "2017-09-11-" + filename)))
        self.assertRegex(self.getPDFText(os.path.join(self.workingDir, "2017-09-11-" + filename)), "Some PDF content")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    @freeze_time("2015-02-03 14:00:00")
    def test_plaincontent_timedfileexist(self):
        self.attachText("Hello!")
        filename1 = os.path.join(self.workingDir, self.getTimeStamp(datetime.now()) + ".pdf")
        filename2 = os.path.join(self.workingDir, self.getTimeStamp(datetime.now()) + "_1.pdf")
        self.touch(os.path.join(self.workingDir, filename1))
        self.assertTrue(os.path.exists(filename1))
        self.assertFalse(os.path.exists(filename2))
        error = self.invokeDirectly()
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(filename1))
        self.assertTrue(os.path.exists(filename2))
        self.assertIsNone(self.getPDFText(filename1))
        self.assertRegex(self.getPDFText(filename2), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
