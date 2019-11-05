from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


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
    saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    if 'next' in request.GET:
        redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + request.GET['next']
    else:
        redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + settings.SAML_LOGIN_REDIRECT
    url = saml_auth.login(redirect_to)
    request.session['AuthNRequestID'] = saml_auth.get_last_request_id()
    return HttpResponseRedirect(url)


def logout(request):
    req = prepare_django_request(request)
    saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    name_id = request.session.get('samlNameId', None)
    session_index = request.session.get('samlSessionIndex', None)
    name_id_format = request.session.get('samlNameIdFormat', None)
    name_id_nq = request.session.get('samlNameIdNameQualifier', None)
    name_id_spnq = request.session.get('samlNameIdSPNameQualifier', None)
    auth.logout(request)
    url = saml_auth.logout(
        name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq,
        return_to=settings.SAML_LOGOUT_REDIRECT
    )
    return HttpResponseRedirect(url)


def saml_sls(request):
    req = prepare_django_request(request)
    saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    request_id = request.session.get('LogoutRequestID', None)
    url = saml_auth.process_slo(request_id=request_id, delete_session_cb=lambda: request.session.flush())
    errors = saml_auth.get_errors()
    if len(errors) == 0:
        auth.logout(request)
        if url is not None:
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(settings.SAML_LOGOUT_REDIRECT)


@csrf_exempt
def saml_acs(request):
    req = prepare_django_request(request)
    saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
    request_id = request.session.get('AuthNRequestID', None)
    saml_auth.process_response(request_id=request_id)

    errors = saml_auth.get_errors()

    if not errors:
        user = auth.authenticate(session_data=saml_auth.get_attributes())
        if user is None:
            raise PermissionDenied()
        auth.login(request, user)
        # This data is used during Single Log Out
        request.session['samlNameId'] = saml_auth.get_nameid()
        request.session['samlNameIdFormat'] = saml_auth.get_nameid_format()
        request.session['samlNameIdNameQualifier'] = saml_auth.get_nameid_nq()
        request.session['samlNameIdSPNameQualifier'] = saml_auth.get_nameid_spnq()
        request.session['samlSessionIndex'] = saml_auth.get_session_index()
        if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
            url = saml_auth.redirect_to(req['post_data']['RelayState'])
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(settings.SAML_LOGIN_REDIRECT)
    return HttpResponseServerError(content=', '.join(errors))


def metadata(request):
    metadata = settings.ONELOGIN_SAML_SETTINGS.get_sp_metadata()
    errors = settings.ONELOGIN_SAML_SETTINGS.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type='text/xml')
    else:
        resp = HttpResponseServerError(content=', '.join(errors))
    return resp
