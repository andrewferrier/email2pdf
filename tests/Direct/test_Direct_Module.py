from tests import BaseTestClasses


class Direct_Module(BaseTestClasses.Email2PDFTestCase):
    def setUp(self):
        super(Direct_Module, self).setUp()

    def test_import(self):
        import email2pdf
        self.assertEqual(email2pdf.WKHTMLTOPDF_EXTERNAL_COMMAND, 'wkhtmltopdf')
