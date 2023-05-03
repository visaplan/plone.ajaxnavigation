"""\
visaplan.plone.ajaxnavigation: exception classes
"""


class AjaxnavError(Exception):
    """
    Root exception class for the visaplan.plone.ajaxnavigation package
    """

class AjaxnavTypeError(TypeError, AjaxnavError):
    """
    Some visaplan.plone.ajaxnavigation component has been used wrongly
    """

class ToolNotFound(AjaxnavError):
    pass

class TemplateNotFound(AjaxnavError):
    pass
