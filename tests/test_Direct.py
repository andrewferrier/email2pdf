from email.message import Message

import os
import tempfile

from tests import BaseTestClasses


class Direct(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct, self).setUp()
        self.msg = Message()

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeDirectly()
        # self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)

    def test_dontPrintBody(self):
        (rc, output, error) = self.invokeDirectly(extraParams=['--no-body'])
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*or.*attachments")

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        unused_f_handle, f_path = tempfile.mkstemp()
        with self.assertRaisesRegex(Exception, "file.*exist"):
            (rc, output, error) = self.invokeDirectly(outputFile=f_path)
        os.unlink(f_path)
