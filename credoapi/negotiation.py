from rest_framework.negotiation import BaseContentNegotiation

JSON_CONTENT = 'application/json'


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    def select_parser(self, request, parsers):
        json_parsers = filter(lambda x: x.media_type == JSON_CONTENT, parsers)
        return json_parsers[0]

    def select_renderer(self, request, renderers, format_suffix):
        json_renderers = filter(lambda x: x.media_type == JSON_CONTENT, renderers)

        return (json_renderers[0], json_renderers[0].media_type)
