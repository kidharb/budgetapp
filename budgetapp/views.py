from django.shortcuts import render, redirect, get_object_or_404
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException
from django.contrib.auth import login as auth_login
from django.http import HttpResponse
import datetime
import pandas as pd
from io import StringIO
from .forms import CSVUploadForm
import logging
from django.utils import timezone
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import CSVContent
from .serializers import CSVContentSerializer
from django.http import JsonResponse

logger = logging.getLogger('django')

class CSVContentViewSet(viewsets.ModelViewSet):
    queryset = CSVContent.objects.all()
    serializer_class = CSVContentSerializer

    @action(detail=True, methods=['delete'])
    def delete_transaction(self, request, pk=None):
        csv = get_object_or_404(CSVContent, id=pk)
        csv.delete()
        return Response({'message': 'Transaction deleted successfully!'}, status=200)

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

            # Validate and process CSV content
            csv_data = StringIO(csv_text)
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

                # Convert 'Transaction Date' to timezone-aware datetime
                df['Transaction Date'] = df['Transaction Date'].apply(lambda x: timezone.make_aware(datetime.datetime.strptime(x, '%Y-%m-%d %H:%M'), timezone=pytz.UTC) if isinstance(x, str) else x)

                # Save each row to the database, excluding 'Nr'
                for _, row in df.iterrows():
                    # Ensure correct data type for numerical values and handle empty strings
                    row['Money In'] = float(row['Money In']) if row['Money In'] != '' else 0.0
                    row['Money Out'] = float(row['Money Out']) if row['Money Out'] != '' else 0.0
                    row['Fee'] = float(row['Fee']) if row['Fee'] != '' else 0.0
                    row['Balance'] = float(row['Balance']) if row['Balance'] != '' else 0.0

                    # Check for existing record
                    existing = CSVContent.objects.filter(
                        transaction_date=row['Transaction Date'],
                    ).exists()

                    if not existing:
                        csv_content = CSVContent(
                            account_number=row['Account'],
                            posting_date=row['Posting Date'],
                            transaction_date=row['Transaction Date'],
                            description=row['Description'],
                            original_description=row['Original Description'],
                            category=row['Category'],
                            money_in=row['Money In'],
                            money_out=row['Money Out'],
                            fees=row['Fee'],
                            balance=row['Balance']
                        )
                        csv_content.save()
                    else:
                        continue
            except Exception as e:
                return HttpResponse(f"Error processing CSV data: {e}")

            return redirect('view_transactions')
    else:
        form = CSVUploadForm()

    return render(request, 'upload.html', {'form': form})

def plot_balance_graph(request):
    transactions = CSVContent.objects.all().order_by('transaction_date')  # Sorting in ascending order for the graph
    dates = [transaction.transaction_date for transaction in transactions]
    balances = [transaction.balance for transaction in transactions]

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

def view_transactions(request):
    transactions = CSVContent.objects.all().order_by('-transaction_date')  # Sorting by Transaction Date
    return render(request, 'view_transactions.html', {'transactions': transactions})

def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(CSVContent, id=transaction_id)
    transaction.delete()
    return redirect('view_transactions')

def delete_all_transactions(request):
    try:
        CSVContent.objects.all().delete()
        return JsonResponse({'message': 'All transactions deleted successfully!'}, status=200)
    except Exception as e:
        return JsonResponse({'message': 'Error deleting transactions', 'error': str(e)}, status=500)

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
