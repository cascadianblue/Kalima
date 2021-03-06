from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView, FormView
from Dictionary.models import Word, Pattern
from Dictionary.forms import WordForm, PatternForm, PatternApplyForm


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['words'] = Word.objects.order_by('?')
        context['patterns'] = Pattern.objects.order_by('?')
        return context


class WordView(DetailView):
    template_name = 'word.html'
    model = Word


class AddWordView(CreateView):
    template_name = 'add_word.html'
    model = Word
    form_class = WordForm


def view_pattern(request, pk):
    '''Detail view for pattern.
    '''
    context = {'pattern': get_object_or_404(Pattern, pk=pk)}
    return render(request, 'pattern.html', context)


def add_pattern(request):
    '''(View) add a pattern using the POST data, if it is valid, then redirect
    to it. If the POST data is not valid, render a page with the invalid fields
    marked.
    '''
    if request.method == 'POST':
        form = PatternForm(request.POST)
        if form.is_valid():
            pattern = form.save()
            return redirect('main:pattern', pk=pattern.pk)
    else:
        form = PatternForm()
    context = {'form': form}
    return render(request, 'add_pattern.html', context)


def edit_pattern(request, pk):
    '''Edit view for pattern
    '''
    pattern = get_object_or_404(Pattern, pk=pk)
    if request.method == 'POST':
        form = PatternForm(request.POST, instance=pattern)
        if form.is_valid():
            form.save(commit=True)
            return redirect('main:pattern', pk=pattern.pk)
    else:
        form = PatternForm(instance=pattern)
    context = {'pattern': pattern, 'form': form}
    return render(request, 'edit_pattern.html', context)


def apply_pattern(request, pk):
    '''View to apply the pattern with id <pk> to the word selected via the
    attached form (instance of PatternApplyForm), and save the result to DB.
    '''
    pattern = get_object_or_404(Pattern, pk=pk)
    if request.method == 'POST':
        form = PatternApplyForm(request.POST)
        if form.is_valid():
            new_word = form.apply(pattern)
            return redirect('main:word', pk=new_word.pk)
    else:
        form = PatternApplyForm()
        queryset = form.fields['stem'].queryset 
        queryset = queryset.filter(pos=pattern.origin_pos)
        # TODO: generate a regex for spellings that match the origin form of
        # this pattern and filter the queryset with it
    context = {'pattern': pattern, 'form': form}
    return render(request, 'apply_pattern.html', context)

def delete_pattern(request, pk):
    '''Delete the Pattern with personal key <pk> (confirmation page on GET,
    perform deletion on POST).
    '''
    pattern = get_object_or_404(Pattern, pk=pk)
    context = {'pattern': pattern}
    if request.method == 'POST':
        pattern.delete()
        return redirect('main:home')
    else:
        return render(request, 'delete_pattern.html', context)
