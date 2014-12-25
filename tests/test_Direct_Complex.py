from datetime import datetime
from email.message import Message
from freezegun import freeze_time

import os

from tests import BaseTestClasses


class Direct_Complex(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Complex, self).setUp()
        self.msg = Message()

    @freeze_time("2015-02-03 14:00:00")
    def test_plaincontent_timedfileexist(self):
        self.setPlainContent("Hello!")
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
