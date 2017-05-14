# -*- coding: utf-8 -*-

from django.views.generic.edit import FormView


class AddTreeProblemView(FormView):

    form_class = None


def report_tree_problem_func(request, *args, **kwargs):
    print(request.POST, args, kwargs)
