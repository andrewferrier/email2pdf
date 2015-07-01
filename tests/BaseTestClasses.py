from PyPDF2 import PdfFileReader
from datetime import datetime
from datetime import timedelta
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.pdftypes import PSException
from reportlab.pdfgen import canvas
from subprocess import Popen, PIPE

import io
import imghdr
import logging
import inspect
import os
import os.path
import requests
import shutil
import sys
import tempfile
import unittest


class Email2PDFTestCase(unittest.TestCase):
    isOnline = None
    examineDir = None

    NONEXIST_IMG = 'http://www.andrewferrier.com/nonexist.jpg'
    NONEXIST_IMG_BLACKLIST = 'http://www.emltrk.com/nonexist.jpg'
    EXIST_IMG = 'https://raw.githubusercontent.com/andrewferrier/email2pdf/master/tests/basi2c16.png'
    EXIST_IMG_UPPERCASE = 'https://raw.githubusercontent.com/andrewferrier/email2pdf/master/tests/UPPERCASE.png'
    COMMAND = os.path.normpath(os.path.join(os.getcwd(), 'email2pdf'))

    DEFAULT_FROM = "from@example.org"
    DEFAULT_TO = "to@example.org"
    DEFAULT_SUBJECT = "Subject of the email"

    JPG_FILENAME = 'tests/jpeg444.jpg'
    PNG_FILENAME = 'tests/basi2c16.png'

    JPG_SIZE = os.path.getsize(JPG_FILENAME)
    PNG_SIZE = os.path.getsize(PNG_FILENAME)

    def setUp(self):
        self.workingDir = tempfile.mkdtemp(dir='/tmp')
        self._check_online()
        self._check_examine_dir()

    def getTimeStamp(self, myTime):
        return myTime.strftime("%Y-%m-%dT%H-%M-%S")

    def existsByTime(self, path=None):
        if self.getTimedFilename(path):
            return True
        else:
            return False

    def getTimedFilename(self, path=None):
        if path is None:
            path = self.workingDir

        for single_time in self._timerange(self.timeInvoked, self.timeCompleted):
            filename = os.path.join(path, self.getTimeStamp(single_time) + ".pdf")
            if os.path.exists(filename):
                return filename

        return None

    def addHeaders(self, frm=DEFAULT_FROM, to=DEFAULT_TO, subject=DEFAULT_SUBJECT, subject_encoding=None):
        if subject:
            if subject_encoding:
                assert isinstance(subject, bytes)
                header = Header(subject, subject_encoding)
                self.msg['Subject'] = header
            else:
                assert isinstance(subject, str)
                self.msg['Subject'] = subject

        if frm:
            self.msg['From'] = frm

        if to:
            self.msg['To'] = to

        self.msg['Date'] = formatdate()

    def invokeAsSubprocess(self, inputFile=False, outputDirectory=None, outputFile=None, extraParams=None,
                           expectOutput=False, okToExist=False):
        bytes_message = self.msg.as_bytes()

        options = [Email2PDFTestCase.COMMAND]

        if inputFile:
            input_file_handle = tempfile.NamedTemporaryFile()
            options.extend(['-i', input_file_handle.name])
            input_file_handle.write(bytes_message)
            input_file_handle.flush()
            my_stdin = None
            my_input = None
        else:
            my_stdin = PIPE
            my_input = bytes_message

        if outputDirectory:
            options.extend(['-d', outputDirectory])

        if outputFile:
            options.extend(['-o', outputFile])
            if not okToExist:
                assert not os.path.exists(outputFile)

        if extraParams is None:
            extraParams = []

        options.extend(extraParams)

        self.timeInvoked = datetime.now()
        if outputDirectory is None:
            my_cwd = self.workingDir
        else:
            my_cwd = None

        p = Popen(options, stdin=my_stdin, stdout=PIPE, stderr=PIPE, cwd=my_cwd)

        output, error = p.communicate(my_input)
        p.wait()
        self.timeCompleted = datetime.now()

        output = str(output, "utf-8")
        error = str(error, "utf-8")

        if expectOutput:
            self.assertNotEqual("", output)
        else:
            self.assertEqual("", output)

        if inputFile:
            input_file_handle.close()

        return (p.returncode, output, error)

    def invokeDirectly(self, outputDirectory=None, outputFile=None, extraParams=None, completeMessage=None, okToExist=False):
        import importlib.machinery
        module_path = self._get_original_script_path()
        loader = importlib.machinery.SourceFileLoader('email2pdf', module_path)
        email2pdf = loader.load_module()

        if completeMessage:
            bytes_message = bytes(completeMessage, 'utf-8')
        else:
            bytes_message = self.msg.as_bytes()

        with tempfile.NamedTemporaryFile() as input_file_handle:
            options = [module_path, '-i', input_file_handle.name]
            input_file_handle.write(bytes_message)
            input_file_handle.flush()

            if outputDirectory:
                options.extend(['-d', outputDirectory])
            else:
                options.extend(['-d', self.workingDir])

            if outputFile:
                options.extend(['-o', outputFile])
                if not okToExist:
                    assert not os.path.exists(outputFile)

            if extraParams is None:
                extraParams = []

            options.extend(extraParams)

            stream = io.StringIO()
            handler = logging.StreamHandler(stream)
            log = logging.getLogger('email2pdf')
            log.propagate = False
            log.setLevel(logging.DEBUG)
            log.addHandler(handler)

            self.timeInvoked = datetime.now()

            try:
                email2pdf.main(options, None, handler)
            finally:
                self.timeCompleted = datetime.now()
                log.removeHandler(handler)
                handler.close()

            error = stream.getvalue()

            return error

    def setPlainContent(self, content, charset='UTF-8'):
        if isinstance(self.msg, MIMEMultipart):
            raise Exception("Cannot call setPlainContent() on a MIME-based message.")
        else:
            self.msg.set_default_type("text/plain")
            self.msg.set_payload(content)
            self.msg.set_charset(charset)

    def attachHTML(self, content, charset=None):
        if not isinstance(self.msg, MIMEMultipart):
            raise Exception("Cannot call attachHTML() on a MIME-based message.")
        else:
            # According to the docs
            # (https://docs.python.org/3.3/library/email.mime.html), setting
            # charset explicitly to None is different from not setting it. Not
            # sure how that works. But for the moment, sticking with this
            # style of invocation to be safe.
            if charset:
                self.msg.attach(MIMEText(content, 'html', charset))
            else:
                self.msg.attach(MIMEText(content, 'html'))

    def attachText(self, content, charset=None):
        if not isinstance(self.msg, MIMEMultipart):
            raise Exception("Cannot call attachText() on a MIME-based message.")
        else:
            if charset:
                self.msg.attach(MIMEText(content, 'plain', charset))
            else:
                self.msg.attach(MIMEText(content, 'plain'))

    def attachPDF(self, string, filePrefix="email2pdf_unittest_file",
                  extension="pdf", mainContentType="application", subContentType="pdf", no_filename=False):
        _, file_name = tempfile.mkstemp(prefix=filePrefix, suffix="." + extension)

        try:
            pdf_canvas = canvas.Canvas(file_name)
            pdf_canvas.drawString(0, 500, string)
            pdf_canvas.save()

            with open(file_name, "rb") as open_handle:
                if no_filename:
                    self.attachAttachment(mainContentType, subContentType, open_handle.read(), None)
                else:
                    self.attachAttachment(mainContentType, subContentType, open_handle.read(), file_name)

            return os.path.basename(file_name)
        finally:
            os.unlink(file_name)

    def attachImage(self, content_id=None, jpeg=True, content_type=None, inline=False, force_filename=False, extension=None):
        if jpeg:
            real_filename = self.JPG_FILENAME
            file_suffix = 'jpg' if not extension else extension
        else:
            real_filename = self.PNG_FILENAME
            file_suffix = 'png' if not extension else extension

        with tempfile.NamedTemporaryFile(prefix="email2pdf_unittest_image", suffix="." + file_suffix) as temp_file:
            _, basic_file_name = os.path.split(temp_file.name)

        with open(real_filename, 'rb') as image_file:
            image = MIMEImage(image_file.read())
            if content_id:
                image.add_header('Content-ID', content_id)
            if content_type:
                self._replace_header(image, 'Content-Type', content_type)

            if inline:
                if force_filename:
                    self._replace_header(image, 'Content-Disposition', 'inline; filename="%s"' % basic_file_name)
                else:
                    self._replace_header(image, 'Content-Disposition', 'inline')
            else:
                self._replace_header(image, 'Content-Disposition', 'attachment; filename="%s"' % basic_file_name)
            self.msg.attach(image)

        if inline and not force_filename:
            return None
        else:
            return basic_file_name

    def attachAttachment(self, mainContentType, subContentType, data, file_name):
        part = MIMEBase(mainContentType, subContentType)
        part.set_payload(data)
        encoders.encode_base64(part)

        if file_name:
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_name))
        else:
            part.add_header('Content-Disposition', 'inline')

        self.msg.attach(part)

    def assertIsJPG(self, filename):
        self.assertEqual(imghdr.what(filename), 'jpeg')

    def getMetadataField(self, pdfFilename, fieldName):
        with open(pdfFilename, 'rb') as file_input:
            input_f = PdfFileReader(file_input)
            documentInfo = input_f.getDocumentInfo()
            key = '/' + fieldName
            if key in documentInfo.keys():
                return documentInfo[key]
            else:
                return None

    def getPDFText(self, filename):
        try:
            with io.StringIO() as retstr:
                with open(filename, 'rb') as filehandle:
                    rsrcmgr = PDFResourceManager()
                    device = TextConverter(rsrcmgr, retstr, laparams=LAParams())
                    pagenos = set()
                    process_pdf(rsrcmgr, device, filehandle, pagenos, maxpages=0, password="", caching=True, check_extractable=True)
                    device.close()
                    string = retstr.getvalue()
                    return string
        except PSException:
            return None

    def touch(self, fname):
        open(fname, 'w').close()

    def find_mount_point(self, path):
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path

    def _timerange(self, start_time, end_time):
        start_time = start_time.replace(microsecond=0)
        end_time = end_time.replace(microsecond=0)
        for step in range(int((end_time - start_time).seconds) + 1):
            yield start_time + timedelta(0, step)

    def _replace_header(self, mimeBase, header, value):
        mimeBase.__delitem__(header)
        mimeBase.add_header(header, value)

    def _get_original_script_path(self):
        module_path = inspect.getfile(inspect.currentframe())
        module_path = os.path.join(os.path.dirname(os.path.dirname(module_path)), 'email2pdf')

        return module_path

    @classmethod
    def _check_examine_dir(cls):
        if Email2PDFTestCase.examineDir is None:
            Email2PDFTestCase.examineDir = '/tmp'
            Email2PDFTestCase.examineDir = tempfile.mkdtemp(dir=Email2PDFTestCase.examineDir)
            print("Output examination directory: " + Email2PDFTestCase.examineDir)

    @classmethod
    def _check_online(cls):
        if Email2PDFTestCase.isOnline is None:
            print("Checking if online... ", end="")
            sys.stdout.flush()
            try:
                request = requests.get(Email2PDFTestCase.EXIST_IMG, headers={'Connection': 'close'})
                request.raise_for_status()
                Email2PDFTestCase.isOnline = True
                print("Yes.")
            except Exception as exception:
                Email2PDFTestCase.isOnline = False
                print("No (" + str(exception) + ")")

    def tearDown(self):
        shutil.rmtree(self.workingDir)
