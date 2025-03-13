from django.views.generic import TemplateView

# Create your views here.
class Home(TemplateView):
    template_name = 'home/home.html'

class Faq(TemplateView):
    template_name = 'faq/faq.html'

class Sponsors(TemplateView):
    template_name = 'sponsors/sponsors.html'