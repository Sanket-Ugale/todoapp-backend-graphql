from django.middleware.csrf import CsrfViewMiddleware

class CustomGraphQLCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path == '/graphql/':
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)