from PyPDF2 import PdfFileReader
from datetime import datetime
from datetime import timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import formatdate
from reportlab.pdfgen import canvas
from subprocess import Popen, PIPE

import os
import requests
import shutil
import sys
import tempfile
import unittest


class Email2PDFTestCase(unittest.TestCase):
    isOnline = None
    examineDir = None

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
            ONLINE_URL = "https://raw.githubusercontent.com/andrewferrier/email2pdf/master"
            try:
                requests.get(ONLINE_URL, timeout=1)
                Email2PDFTestCase.isOnline = True
                print("Yes.")
            except requests.exceptions.RequestException:
                Email2PDFTestCase.isOnline = False
                print("No.")

        return Email2PDFTestCase.isOnline

    def getTimeStamp(self, myTime):
        return myTime.strftime("%Y-%m-%dT%H-%M-%S")

    def existsByTime(self, path=None):
        if path is None:
            path = self.workingDir

        found = False

        for single_time in self.timerange(self.timeInvoked, self.timeCompleted):
            if os.path.exists(os.path.join(path, self.getTimeStamp(single_time) + ".pdf")):
                found = True

        return found

    def addHeaders(self, frm="from@example.org", to="to@example.org", subject="Subject of the email"):
        if(subject):
            self.msg['Subject'] = subject

        if(frm):
            self.msg['From'] = frm

        if(to):
            self.msg['To'] = to

        self.msg['Date'] = formatdate()

    def invokeEmail2PDF(self, inputFile=False, outputDirectory=None, outputFile=None, extraParams=[]):
        textMessage = self.msg.as_string()

        options = [self.command]

        if inputFile:
            inputFile_handle = tempfile.NamedTemporaryFile()
            options.extend(['-i', inputFile_handle.name])
            myStdin = None
            myInput = None
        else:
            myStdin = PIPE
            myInput = bytes(textMessage, 'UTF-8')

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

    def setPlainContent(self, content, charset='UTF-8'):
        self.msg.set_default_type("text/plain")
        self.msg.set_payload(content)
        self.msg.set_charset(charset)

    def attachHTML(self, content):
        self.msg.attach(MIMEText(content, 'html'))

    def attachText(self, content):
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
