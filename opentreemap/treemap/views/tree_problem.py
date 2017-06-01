# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from treemap.forms import TreeProblemForm


def report_tree_problem_func(request, *args, **kwargs):
    if request.user.is_authenticated():
        form = TreeProblemForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
        else:
            # TODO: logging
            print(form.errors)
        return redirect('/')
    return redirect('/accounts/login/')
