from django.db import migrations


def create_initial_categories(apps, schema_editor):
    Category = apps.get_model("events", "CategoryModel")

    initial_categories = [
        "tecnologia",
        "educação",
        "entretenimento",
        "esportes",
        "saúde",
        "finanças",
        "marketing",
        "vendas",
        "recursos humanos",
        "logística",
        "jurídico",
        "segurança da informação",
        "infraestrutura",
        "desenvolvimento de software",
        "devops",
        "inteligência artificial",
        "machine learning",
        "ciência de dados",
        "análise de dados",
        "produtividade",
        "design",
        "ux",
        "ui",
        "administração",
        "gestão de projetos",
        "suporte técnico",
        "atendimento ao cliente",
        "comunicação",
        "publicidade",
        "comércio exterior",
        "e-commerce",
        "operacional",
        "engenharia",
        "qualidade",
        "compliance",
        "auditoria",
        "governança",
        "mobilidade",
        "cloud computing",
        "iot",
        "automação",
        "robótica",
        "energia",
        "meio ambiente",
        "sustentabilidade",
        "agricultura",
        "indústria",
        "telecomunicações",
        "biotecnologia",
        "pesquisa",
    ]

    for name in initial_categories:
        normalized = name.strip().lower()
        Category.objects.get_or_create(name=normalized)


def reverse_initial_categories(apps, schema_editor):
    Category = apps.get_model("events", "CategoryModel")

    categories_to_remove = [
        "tecnologia",
        "educação",
        "entretenimento",
        "esportes",
        "saúde",
        "finanças",
        "marketing",
        "vendas",
        "recursos humanos",
        "logística",
        "jurídico",
        "segurança da informação",
        "infraestrutura",
        "desenvolvimento de software",
        "devops",
        "inteligência artificial",
        "machine learning",
        "ciência de dados",
        "análise de dados",
        "produtividade",
        "design",
        "ux",
        "ui",
        "administração",
        "gestão de projetos",
        "suporte técnico",
        "atendimento ao cliente",
        "comunicação",
        "publicidade",
        "comércio exterior",
        "e-commerce",
        "operacional",
        "engenharia",
        "qualidade",
        "compliance",
        "auditoria",
        "governança",
        "mobilidade",
        "cloud computing",
        "iot",
        "automação",
        "robótica",
        "energia",
        "meio ambiente",
        "sustentabilidade",
        "agricultura",
        "indústria",
        "telecomunicações",
        "biotecnologia",
        "pesquisa",
    ]

    for name in categories_to_remove:
        normalized = name.strip().lower()
        Category.objects.filter(name=normalized).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_eventparticipantmodel_attended_at_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_categories,
            reverse_initial_categories,
        )
    ]
