import os


def generate_pdf_from_html(html_content, output_path):
    try:
        import weasyprint
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        print('PDF generated at: ' + output_path)
        return True
    except ImportError:
        print('WeasyPrint not installed. Skipping PDF generation.')
        return False
    except Exception as e:
        print('PDF generation error: ' + str(e))
        return False


def save_html_report(html_content, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print('HTML report saved at: ' + output_path)
        return True
    except Exception as e:
        print('HTML save error: ' + str(e))
        return False


def get_report_path(base_dir, month, year, format_type='html'):
    filename = 'report_' + str(year) + '_' + str(month).zfill(2) + '.' + format_type
    return os.path.join(base_dir, filename), filename