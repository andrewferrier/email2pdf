from email.message import Message

import os
import tempfile

from tests.BaseTestClasses import Email2PDFTestCase


class TestBasic(Email2PDFTestCase):
    def setUp(self):
        super(TestBasic, self).setUp()
        self.msg = Message()

    def test_simple(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_simple_with_explicit_stdin(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['-i-'])
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_help(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--help'], expectOutput=True)
        self.assertEqual(0, rc)
        self.assertRegex(output, 'usage:')
        self.assertEqual(error, '')
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_invalid_option(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--invalid-option'])
        self.assertEqual(2, rc)
        self.assertRegex(error, 'ERROR: unrecognized.*')
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_dont_print_body(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--no-body'])
        self.assertEqual(1, rc)
        self.assertFalse(self.existsByTime())
        self.assertRegex(error, "body.*any.*attachments")
        self.assertTrue(self.existsByTimeWarning())
        self.assertRegex(self.getWarningFileContents(), "body.*any.*attachments")
        self.assertTrue(self.existsByTimeOriginal())
        self.assertValidOriginalFileContents()

    def test_dont_print_body_mostly_hide_warnings(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--no-body', '--mostly-hide-warnings'])
        self.assertEqual(0, rc)
        self.assertFalse(self.existsByTime())
        self.assertEqual('', error)
        self.assertTrue(self.existsByTimeWarning())
        self.assertRegex(self.getWarningFileContents(), "body.*any.*attachments")
        self.assertTrue(self.existsByTimeOriginal())
        self.assertValidOriginalFileContents()

    def test_no_message_headers(self):
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_no_message_headers_mostly_hide_warnings(self):
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['--mostly-hide-warnings'])
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_withinputfile(self):
        self.addHeaders()
        (rc, output, error) = self.invokeAsSubprocess(inputFile=True)
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_nosubject(self):
        self.addHeaders(Email2PDFTestCase.DEFAULT_FROM, Email2PDFTestCase.DEFAULT_TO, None)
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent(self):
        self.addHeaders()
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_upsidedown(self):
        self.addHeaders()
        self.setPlainContent("ɯɐɹƃoɹd ɟpdᄅlᴉɐɯǝ ǝɥʇ ɟo ʇsǝʇ ɐ sᴉ sᴉɥʇ ollǝH")
        (rc, output, error) = self.invokeAsSubprocess()
        self.assertEqual(0, rc)
        self.assertTrue(self.existsByTime())
        self.assertEqual('', error)
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "ɯɐɹƃoɹd ɟpdᄅlᴉɐɯǝ ǝɥʇ ɟo ʇsǝʇ ɐ sᴉ sᴉɥʇ ollǝH")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_poundsign_iso88591(self):
        self.addHeaders()
        path = os.path.join(self.examineDir, "plaincontent_poundsign_iso88591.pdf")
        self.setPlainContent("Hello - this email costs \xa35!", charset="ISO-8859-1")
        (rc, output, error) = self.invokeAsSubprocess(outputFile=path)
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(os.path.exists(path))
        self.assertRegex(self.getPDFText(path), "Hello - this email costs \xa35!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_notrailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(outputDirectory="/tmp")
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime("/tmp"))
        self.assertRegex(self.getPDFText(self.getTimedFilename("/tmp/")), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_trailingslash(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(outputDirectory="/tmp/")
        self.assertEqual(0, rc)
        self.assertEqual('', error)
        self.assertTrue(self.existsByTime("/tmp/"))
        self.assertRegex(self.getPDFText(self.getTimedFilename("/tmp/")), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_outputfileoverrides(self):
        filename = os.path.join(self.examineDir, "outputFileOverrides.pdf")
        with tempfile.TemporaryDirectory() as pathname:
            self.setPlainContent("Hello!")
            (rc, output, error) = self.invokeAsSubprocess(outputDirectory=pathname, outputFile=filename)
            self.assertEqual(0, rc)
            self.assertEqual('', error)
            self.assertFalse(self.existsByTime(pathname))
            self.assertTrue(os.path.exists(filename))
            self.assertRegex(self.getPDFText(filename), "Hello!")
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())

    def test_plaincontent_fileexist(self):
        self.setPlainContent("Hello!")
        with tempfile.NamedTemporaryFile() as tmpfile:
            (rc, output, error) = self.invokeAsSubprocess(outputFile=tmpfile.name, okToExist=True)
            self.assertEqual(2, rc)
            self.assertRegex(error, "file.*exist")
            self.assertFalse(self.existsByTimeWarning())
            self.assertFalse(self.existsByTimeOriginal())

    def test_verbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['-v'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())

    def test_veryverbose(self):
        self.setPlainContent("Hello!")
        (rc, output, error) = self.invokeAsSubprocess(extraParams=['-vv'])
        self.assertEqual(0, rc)
        self.assertNotEqual('', error)
        self.assertTrue(self.existsByTime())
        self.assertRegex(self.getPDFText(self.getTimedFilename()), "Hello!")
        self.assertFalse(self.existsByTimeWarning())
        self.assertFalse(self.existsByTimeOriginal())
