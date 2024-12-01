from django.shortcuts import render, redirect, get_object_or_404
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.http import HttpResponse
import html
import datetime
import pandas as pd
from io import StringIO
from .forms import CSVUploadForm
import logging
from rest_framework import viewsets
from .models import PDFContent
from .serializers import PDFContentSerializer

logger = logging.getLogger('django')

class PDFContentViewSet(viewsets.ModelViewSet):
    queryset = PDFContent.objects.all()
    serializer_class = PDFContentSerializer

def home(request):
    return render(request, 'home.html')
def remove_duplicates(text):
    if isinstance(text, str):
        words = text.split()
        unique_words = []
        seen = set()
        for word in words:
            if word.lower() not in seen:
                unique_words.append(word)
                seen.add(word.lower())
        return ' '.join(unique_words)
    return text

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST)
        if form.is_valid():
            csv_text = form.cleaned_data['csv_text']

            # Sanitize input
            sanitized_csv_text = html.escape(csv_text)

            # Validate and process CSV content
            csv_data = StringIO(sanitized_csv_text)
            try:
                # Read CSV data with proper handling of empty fields
                df = pd.read_csv(csv_data, delimiter=',', keep_default_na=False)

                # Validate CSV headers
                expected_headers = ['Nr', 'Account', 'Posting Date', 'Transaction Date', 'Description', 'Original Description', 'Category', 'Money In', 'Money Out', 'Fee', 'Balance']
                if list(df.columns) != expected_headers:
                    raise ValueError("Invalid CSV headers")

                # Ensure columns are named appropriately, excluding 'Nr'
                df.columns = expected_headers
                df = df.fillna(0)  # Handle empty numeric fields

                # Remove whitespace and duplicate words from all string fields
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

                # Convert 'Transaction Date' to 24-hour format
                df['Transaction Date'] = df['Transaction Date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M') if isinstance(x, str) else x)

                # Save each row to the database, excluding 'Nr'
                for _, row in df.iterrows():
                    # Ensure correct data type for numerical values and handle empty strings
                    row['Money In'] = float(row['Money In']) if row['Money In'] != '' else 0.0
                    row['Money Out'] = float(row['Money Out']) if row['Money Out'] != '' else 0.0
                    row['Fee'] = float(row['Fee']) if row['Fee'] != '' else 0.0
                    row['Balance'] = float(row['Balance']) if row['Balance'] != '' else 0.0

                    # Check for existing record
                    existing = PDFContent.objects.filter(
                        field4=row['Transaction Date'],
                    ).exists()

                    if not existing:
                        pdf_content = PDFContent(
                            field2=row['Account'],
                            field3=row['Posting Date'],
                            field4=row['Transaction Date'],
                            field5=row['Description'],
                            field6=row['Original Description'],
                            field7=row['Category'],
                            field8=row['Money In'],
                            field9=row['Money Out'],
                            field10=row['Fee'],
                            field11=row['Balance']
                        )
                        pdf_content.save()
                    else:
                        continue
            except Exception as e:
                return HttpResponse(f"Error processing CSV data: {e}")

            return redirect('view_pdfs')
    else:
        form = CSVUploadForm()

    return render(request, 'upload.html', {'form': form})

def plot_balance_graph(request):
    pdfs = PDFContent.objects.all().order_by('field4')  # Sorting in ascending order for the graph
    dates = [pdf.field4 for pdf in pdfs]
    balances = [pdf.field11 for pdf in pdfs]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, balances, marker='o')
    plt.title('Balance Over Time')
    plt.xlabel('Transaction Date')
    plt.ylabel('Balance')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')

def view_pdfs(request):
    pdfs = PDFContent.objects.all().order_by('-field4')  # Assuming field4 is Transaction Date
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
