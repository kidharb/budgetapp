from django.shortcuts import render, redirect, get_object_or_404
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.http import HttpResponse

import pandas as pd
from io import StringIO
from .models import PDFContent
from .forms import CSVUploadForm
import logging

logger = logging.getLogger('django')

def home(request):
    return render(request, 'home.html')

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST)
        if form.is_valid():
            csv_text = form.cleaned_data['csv_text']
            csv_data = StringIO(csv_text)

            try:
                # Read CSV data
                df = pd.read_csv(csv_data, delimiter=',', on_bad_lines='warn')

                # Ensure columns are named appropriately, excluding 'Nr'
                df.columns = ['Nr', 'Account', 'Posting Date', 'Transaction Date', 'Description', 'Original Description', 'Category', 'Money In', 'Money Out', 'Fee', 'Balance']
                df = df.fillna(0)
                logger.debug(df)

                # Save each row to the database, excluding 'Nr'
                for _, row in df.iterrows():
                    # Check for existing record
                    existing = PDFContent.objects.filter(
                        field4=row['Transaction Date'],
                    ).exists()

                    if not existing:
                        pdf_content = PDFContent(
                            field4=row['Transaction Date'],
                        )
                        pdf_content.save()
                    else:
                        logger.warning(f"Duplicate entry found: {row['Account']}, {row['Posting Date']}")
                        continue
            except Exception as e:
                return HttpResponse(f"Error processing CSV data: {e}")

            return redirect('view_pdfs')
    else:
        form = CSVUploadForm()

    return render(request, 'upload.html', {'form': form})

def view_pdfs(request):
    pdfs = PDFContent.objects.all()
    return render(request, 'view_pdfs.html', {'pdfs': pdfs})

def delete_pdf(request, pdf_id):
    pdf = get_object_or_404(PDFContent, id=pdf_id)
    pdf.delete()
    return redirect('view_pdfs')

def google_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('social:begin', backend='google-oauth2')

def callback(request):
    strategy = load_strategy(request)
    backend = load_backend(strategy, 'google-oauth2', redirect_uri=None)
    try:
        user = backend.do_auth(request.GET['code'])
        auth_login(request, user)
        return redirect('home')
    except (MissingBackend, AuthException):
        return HttpResponse("Authentication failed.")
