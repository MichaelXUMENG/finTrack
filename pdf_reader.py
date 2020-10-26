from PyPDF2.pdf import PdfFileReader
from pdfminer.high_level import extract_text, extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO


def extract_pdf_pypdf2(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        if pdf.isEncrypted:
            pdf.decrypt('')
        page_obj = pdf.getPage(2)
        return page_obj.extractText()


def extract_pdf_pdfminer(pdf_path):
    return extract_text(pdf_path)


def extract_pdf_pdfminer_format_with_output(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=LAParams(), output_type='html', codec=None)
        context = output_string.getvalue()
    with open('context.html', 'w') as fd:
        fd.write(output_string.getvalue())
    return context


def extract_pdf_pdfminer_format_without_output(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=LAParams(), output_type='html', codec=None)
        context = output_string.getvalue()
    return context
