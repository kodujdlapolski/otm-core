
from django import forms

from treemap.models import TreeProblem


class TreeProblemForm(forms.ModelForm):

    """
    Form for saving tree problem on the tree instance.
    """

    class Meta:
        model = TreeProblem
        fields = ['tree_problem', 'tree', 'description', ]
