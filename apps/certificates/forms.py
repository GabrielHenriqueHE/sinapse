from django import forms

from apps.certificates.models import CertificateTemplateModel


class CertificateTemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplateModel
        fields = ["name", "width", "height", "html_content"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300",
                    "placeholder": "Digite o nome do template",
                }
            ),
            "width": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300",
                    "min": "100",
                    "max": "2000",
                }
            ),
            "height": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300",
                    "min": "100",
                    "max": "2000",
                }
            ),
            "html_content": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300 font-mono text-sm",
                    "rows": 20,
                    "placeholder": "Digite o HTML do certificado aqui...",
                }
            ),
            "logo": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "name": "Nome do Template",
            "width": "Largura (px)",
            "height": "Altura (px)",
            "html_content": "Conteúdo HTML",
        }

    def clean_width(self):
        width = self.cleaned_data.get("width")
        if width < 100:
            raise forms.ValidationError("A largura mínima é 100px")
        if width > 2000:
            raise forms.ValidationError("A largura máxima é 2000px")
        return width

    def clean_height(self):
        height = self.cleaned_data.get("height")
        if height < 100:
            raise forms.ValidationError("A altura mínima é 100px")
        if height > 2000:
            raise forms.ValidationError("A altura máxima é 2000px")
        return height

    def clean_html_content(self):
        html_content = self.cleaned_data.get("html_content")
        if not html_content:
            raise forms.ValidationError("O conteúdo HTML é obrigatório")
        return html_content
