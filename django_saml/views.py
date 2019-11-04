from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth


def prepare_django_request(request):
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return result


def login(request):
    req = prepare_django_request(request)
    auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    if 'next' in request.GET:
        url = auth.login() + request.GET['next']
    else:
        url = auth.login()
    return HttpResponseRedirect(url)


@csrf_exempt
def saml_acs(request):
    req = prepare_django_request(request)
    auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    request_id = None
    if 'AuthNRequestID' in request.session:
        request_id = request.session['AuthNRequestID']
    auth.process_response(request_id=request_id)

    errors = auth.get_errors()

    if not errors:
        print(auth.get_attributes())
        print(auth.get_nameid_format())
        print(auth.get_nameid())
        return HttpResponse(auth.get_attributes(), "Response")
        if 'AuthNRequestID' in request.session:
            del request.session['AuthNRequestID']
        request.session['samlUserdata'] = auth.get_attributes()
        request.session['samlNameId'] = auth.get_nameid()
        request.session['samlNameIdFormat'] = auth.get_nameid_format()
        request.session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
        request.session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
        request.session['samlSessionIndex'] = auth.get_session_index()
        if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
            return HttpResponseRedirect(auth.redirect_to(req['post_data']['RelayState']))
    return HttpResponseServerError(content=', '.join(errors))


def metadata(request):
    metadata = settings.ONELOGIN_SAML_SETTINGS.get_sp_metadata()
    errors = settings.ONELOGIN_SAML_SETTINGS.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp
