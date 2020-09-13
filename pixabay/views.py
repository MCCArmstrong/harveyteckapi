from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from .forms import PixaForm, UsersSignupForm, Authentication
from .models import UploadFile
import requests
from django.contrib.auth import views as auth_views
from .api import pixabay_api


class AjaxableResponseMixin:
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class BaseHome(TemplateView):
    template_name = 'admin/index.html'
    queryset = UploadFile.objects.all().order_by("id")[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ImageList(ListView):
    template_name = 'admin/file_list.html'
    queryset = UploadFile.objects.all().order_by("id")[:4]


class FileUpload(AjaxableResponseMixin, CreateView):
    template_name = 'admin/file.html'
    form_class = PixaForm
    success_url = reverse_lazy("pixabay:image-panel")


class PixabaySearch(AjaxableResponseMixin, TemplateView):
    template_name = 'admin/baysearch.html'

    def get_queryset(self, request, *args, **kwargs):
        query = self.request.GET('q')
        if query.is_valid():
            api_key = '18254741-ce7f3e60a43d460c4e262ec4f'
            url = "https://pixabay.com/api/"
            query = 'lagos'
            PER_PAGE = 200
            callback_url = request.build_absolute_uri(str(reverse_lazy('pixabay:bay-search')))

            PARAMS = {'q': query, 'per_page': PER_PAGE, 'page': 1}
            end_point = url + "?key" + api_key
            # url_link = []
            fields = {
                'callback_url': callback_url
            }
            header = {
                'Authorization': 'Bearer %s' % api_key,
                'Content-Type': 'application/json',
                'Cache-control': 'no-cache'
            }
            req = requests.get(url=end_point, params=PARAMS, headers=header, json=fields)
            data = req.json()
            # return data
            if data['status']:
                redirect_url = data['data']['authorization_url']
                return HttpResponseRedirect(redirect_url)


class UpdateFile(AjaxableResponseMixin, UpdateView):
    model = UploadFile
    success_url = reverse_lazy('pixabay:image-panel')
    template_name = 'admin/file.html'
    form_class = PixaForm


class FileDelete(DeleteView):
    model = UploadFile
    success_url = reverse_lazy("pixabay:image-panel")
    template_name = 'admin/file_list.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return super().post(self, *args, **kwargs)
        return super().dispatch()


def searchImage(request):
    search_keyword = request.GET['query']
    search_result = UploadFile.objects.filter(
        Q(file_name__icontains=search_keyword) | Q(file_format__icontains=search_keyword)).values('file_name',
                                                                                                  'file_format')
    search_result = list(search_result)
    return JsonResponse(search_result, safe=False)
