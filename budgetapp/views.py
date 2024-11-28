from django.shortcuts import render, redirect
from django.http import HttpResponse
from PyPDF2 import PdfReader
import io
from .models import PDFContent
from .forms import PDFUploadForm

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf']
            pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
            text = ''
            for page_number in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_number]
                text += page.extract_text()

            # Save parsed content to the database
            pdf_content = PDFContent(title=pdf_file.name, content=text)
            pdf_content.save()
            return redirect('view_pdfs')

    else:
        form = PDFUploadForm()

    return render(request, 'upload.html', {'form': form})

def view_pdfs(request):
    pdfs = PDFContent.objects.all()
    return render(request, 'view_pdfs.html', {'pdfs': pdfs})

def home(request):
    return render(request, 'home.html')
