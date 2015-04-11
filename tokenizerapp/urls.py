from django.conf.urls import patterns, include, url
from django.contrib import admin
from categorizer import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tokenizerapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','categorizer.views.index',name='index'),
    url(r'^tokenizer/$','categorizer.views.tokenizer',name='tokenizer'),
    url(r'^stemmer/$','categorizer.views.stemmer',name='stemmer'),
    url(r'^stopwords/$','categorizer.views.stop_word_remover',name='stop_words_remover'),
    url(r'^freq/$','categorizer.views.freq',name='freq'),
    url(r'^classify/$','categorizer.views.classify',name='classify'),
    url(r'^suggest/$','categorizer.views.suggest',name='suggest'),

)
