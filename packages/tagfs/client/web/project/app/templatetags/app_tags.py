from django import template
from django.conf import settings

register = template.Library()

CLIENT = settings.TAGFSCLIENT

class PopularTagsNode(template.Node):
    def __init__(self, number, context_var):
        self.number = number
        self.context_var = context_var

    def render(self, context):
        try:
            number = template.resolve_variable(self.number, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = CLIENT.get_popular_tags(number)
        return ''


class FileInfoNode(template.Node):
    def __init__(self, file_hash, context_var):
        self.file_hash = file_hash
        self.context_var = context_var

    def render(self, context):
        try:
            file_hash = template.resolve_variable(self.file_hash, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = CLIENT.info(file_hash)
        return ''


def do_get_popular_tags(parser, token):
    """
    Retrieves the popular tags.

    Example usage::

        {% get_popular_tags number as popular_tags %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return PopularTagsNode(bits[1], bits[3])

def do_get_file_info(parser, token):
    """
    Retrieves the file info.

    Example usage::

        {% get_file_info file_hash as file_info %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return FileInfoNode(bits[1], bits[3])


register.tag('get_popular_tags', do_get_popular_tags)
register.tag('get_file_info', do_get_file_info)