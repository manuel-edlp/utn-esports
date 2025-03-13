from django.views.generic import TemplateView

# Create your views here.
class Home(TemplateView):
    template_name = 'home/home.html'

class Faq(TemplateView):
    template_name = 'faq/faq.html'