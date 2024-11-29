from django import forms

class CSVUploadForm(forms.Form):
    csv_text = forms.CharField(widget=forms.Textarea, label='CSV Text')
