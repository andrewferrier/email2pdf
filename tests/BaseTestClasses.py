from PyPDF2 import PdfFileReader
from datetime import datetime
from datetime import timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from reportlab.pdfgen import canvas
from subprocess import Popen, PIPE

import io
import logging
import inspect
import os
import requests
import shutil
import sys
import tempfile
import unittest


class Email2PDFTestCase(unittest.TestCase):
    isOnline = None
    examineDir = None

    NONEXIST_IMG = 'http://www.andrewferrier.com/nonexist.jpg'
    EXIST_IMG = 'https://raw.githubusercontent.com/andrewferrier/email2pdf/master/tests/basi2c16.png'

    def setUp(self):
        self.workingDir = tempfile.mkdtemp(dir='/tmp')
        self.command = os.path.normpath(os.path.join(os.getcwd(), 'email2pdf'))
        self.checkOnline()
        self.checkExamineDir()

    @classmethod
    def checkExamineDir(cls):
        if Email2PDFTestCase.examineDir is None:
            Email2PDFTestCase.examineDir = '/tmp'
            Email2PDFTestCase.examineDir = tempfile.mkdtemp(dir=Email2PDFTestCase.examineDir)
            print("Output examination directory: " + Email2PDFTestCase.examineDir)

    @classmethod
    def checkOnline(cls):
        if Email2PDFTestCase.isOnline is None:
            print("Checking if online... ", end="")
            sys.stdout.flush()
            try:
                r = requests.get(Email2PDFTestCase.EXIST_IMG, headers={'Connection': 'close'})
                r.raise_for_status()
                Email2PDFTestCase.isOnline = True
                print("Yes.")
            except Exception as e:
                Email2PDFTestCase.isOnline = False
                print("No (" + str(e) + ")")

    def getOriginalScriptPath(self):
        module_path = inspect.getfile(inspect.currentframe())
        module_path = os.path.join(os.path.dirname(os.path.dirname(module_path)), 'email2pdf')

        return module_path

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

        for single_time in self.timerange(self.timeInvoked, self.timeCompleted):
            filename = os.path.join(path, self.getTimeStamp(single_time) + ".pdf")
            if os.path.exists(filename):
                return filename

        return None

    def addHeaders(self, frm="from@example.org", to="to@example.org", subject="Subject of the email"):
        if(subject):
            self.msg['Subject'] = subject

        if(frm):
            self.msg['From'] = frm

        if(to):
            self.msg['To'] = to

        self.msg['Date'] = formatdate()

    def invokeAsSubprocess(self, inputFile=False, outputDirectory=None, outputFile=None, extraParams=[]):
        bytesMessage = self.msg.as_bytes()

        options = [self.command]

        if inputFile:
            inputFile_handle = tempfile.NamedTemporaryFile()
            options.extend(['-i', inputFile_handle.name])
            inputFile_handle.write(bytesMessage)
            inputFile_handle.flush()
            myStdin = None
            myInput = None
        else:
            myStdin = PIPE
            myInput = bytesMessage

        if outputDirectory:
            options.extend(['-d', outputDirectory])

        if outputFile:
            options.extend(['-o', outputFile])

        options.extend(extraParams)

        self.timeInvoked = datetime.now()
        if outputDirectory is None:
            myCwd = self.workingDir
        else:
            myCwd = None

        p = Popen(options, stdin=myStdin, stdout=PIPE, stderr=PIPE, cwd=myCwd)

        output, error = p.communicate(myInput)
        p.wait()
        self.timeCompleted = datetime.now()

        output = str(output, "utf-8")
        error = str(error, "utf-8")

        self.assertEqual("", output)

        if inputFile:
            inputFile_handle.close()

        return (p.returncode, output, error)

    def invokeDirectly(self, outputDirectory=None, outputFile=None, extraParams=[]):
        import importlib.machinery
        module_path = self.getOriginalScriptPath()
        loader = importlib.machinery.SourceFileLoader('email2pdf', module_path)
        email2pdf = loader.load_module()

        bytesMessage = self.msg.as_bytes()

        with tempfile.NamedTemporaryFile() as inputFile_handle:
            options = [module_path, '-i', inputFile_handle.name]
            inputFile_handle.write(bytesMessage)
            inputFile_handle.flush()

            if outputDirectory:
                options.extend(['-d', outputDirectory])
            else:
                options.extend(['-d', self.workingDir])

            if outputFile:
                options.extend(['-o', outputFile])

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

    def attachHTML(self, content):
        if not isinstance(self.msg, MIMEMultipart):
            raise Exception("Cannot call attachHTML() on a MIME-based message.")
        else:
            self.msg.attach(MIMEText(content, 'html'))

    def attachText(self, content):
        if not isinstance(self.msg, MIMEMultipart):
            raise Exception("Cannot call attachText() on a MIME-based message.")
        else:
            self.msg.attach(MIMEText(content, 'plain'))

    def attachPDF(self, string, filePrefix="email2pdf_unittest_file",
                  extension="pdf", mainContentType="application", subContentType="pdf"):
        unused_f_handle, file_name = tempfile.mkstemp(prefix=filePrefix, suffix="." + extension)

        try:
            cv = canvas.Canvas(file_name)
            cv.drawString(0, 500, string)
            cv.save()

            openHandle = open(file_name, "rb")
            self.attachAttachment(mainContentType, subContentType, openHandle.read(), file_name)
            openHandle.close()

            return os.path.basename(file_name)
        finally:
            os.unlink(file_name)

    def attachImage(self, content_id=None, jpeg=True, content_type=None, inline=False, extension=None):
        if jpeg:
            realFilename = 'tests/jpeg444.jpg'
            fileSuffix = 'jpg' if not extension else extension
        else:
            realFilename = 'tests/basi2c16.png'
            fileSuffix = 'png' if not extension else extension

        unused_f_handle, file_name = tempfile.mkstemp(prefix="email2pdf_unittest_image", suffix="." + fileSuffix)
        unused_path, basic_file_name = os.path.split(file_name)

        with open(realFilename, 'rb') as image_file:
            image = MIMEImage(image_file.read())
            if content_id:
                image.add_header('Content-ID', content_id)
            if content_type:
                self.replace_header(image, 'Content-Type', content_type)

            if inline:
                self.replace_header(image, 'Content-Disposition', 'inline')
            else:
                self.replace_header(image, 'Content-Disposition', 'attachment; filename="%s"' % basic_file_name)
            self.msg.attach(image)

        if inline:
            return None
        else:
            return basic_file_name

    def attachAttachment(self, mainContentType, subContentType, data, file_name):
        part = MIMEBase(mainContentType, subContentType)
        part.set_payload(data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_name))
        self.msg.attach(part)

    def getMetadataField(self, pdfFilename, fieldName):
        with open(pdfFilename, 'rb') as file_input:
            inputF = PdfFileReader(file_input)
            documentInfo = inputF.getDocumentInfo()
            key = '/' + fieldName
            if(key in documentInfo.keys()):
                return documentInfo[key]
            else:
                return None

    def getPDFText(self, filename):
        try:
            with io.StringIO() as retstr:
                with open(filename, 'rb') as fp:
                    rsrcmgr = PDFResourceManager()
                    device = TextConverter(rsrcmgr, retstr, laparams=LAParams())
                    pagenos = set()
                    process_pdf(rsrcmgr, device, fp, pagenos, maxpages=0, password="", caching=True, check_extractable=True)
                    device.close()
                    string = retstr.getvalue()
                    return string
        except:
            return None

    def touch(self, fname):
        open(fname, 'w').close()

    def timerange(self, start_time, end_time):
        start_time = start_time.replace(microsecond=0)
        end_time = end_time.replace(microsecond=0)
        for n in range(int((end_time - start_time).seconds) + 1):
            yield start_time + timedelta(0, n)

    def find_mount_point(self, path):
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path

    def replace_header(self, mimeBase, header, value):
        mimeBase.__delitem__(header)
        mimeBase.add_header(header, value)

    def tearDown(self):
        shutil.rmtree(self.workingDir)
