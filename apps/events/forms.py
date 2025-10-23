# events/forms.py
from django import forms

from apps.events.models import EventModel


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = [
            "name",
            "description",
            "topics",
            "street",
            "complement",
            "city",
            "state",
            "country",
            "zip_code",
            "start_date",
            "end_date",
            "participants_limit",
            "category",
            "image_url",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Tech Conference 2024",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Descreva seu evento de forma atraente...",
                    "rows": 4,
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300 resize-none",
                }
            ),
            "topics": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Tecnologia, Inovação, IA, Blockchain",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "street": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Avenida Paulista, 1234",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "complement": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Sala 501, Bloco B, Andar 5",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "placeholder": "Ex: São Paulo",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "placeholder": "Ex: São Paulo",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Brasil",
                    "value": "Brasil",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "placeholder": "Ex: 01310100",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "start_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "end_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "participants_limit": forms.NumberInput(
                attrs={
                    "placeholder": "Ex: 100",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300"
                }
            ),
            "image_url": forms.URLInput(
                attrs={
                    "placeholder": "https://exemplo.com/imagem.jpg",
                    "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topics"].help_text = "Separe os tópicos com vírgula"
        self.fields["participants_limit"].required = False

    def clean_topics(self):
        topics = self.cleaned_data.get("topics", "")
        return topics if topics else []

    def clean_participants_limit(self):
        participants_limit = self.cleaned_data.get("participants_limit")
        if participants_limit == "" or participants_limit is None:
            return None
        return participants_limit

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(
                "A data de término deve ser posterior à data de início."
            )

        return cleaned_data
