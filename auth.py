import flask
import functools
import json
import urlparse
from flask_oauthlib import client

from common import pattern


def authorized_only(f):

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    if flask.request.remote_addr.startswith('192.168.86.'):
      return f(*args, **kwargs)
    else:
      return flask.current_app.auth.authorize(f, *args, **kwargs)

  return wrapper


class Options(object):

  def __init__(self, client_id, client_secret, callback_url, session_secret):
    self._client_id = client_id
    self._client_secret = client_secret
    self._callback_url = callback_url
    self._session_secret = session_secret

  @property
  def client_id(self):
    return self._client_id

  @property
  def client_secret(self):
    return self._client_secret

  @property
  def callback_url(self):
    return self._callback_url

  @property
  def session_secret(self):
    return self._session_secret

  @classmethod
  def load_from_json(cls, filename):
    with open(filename) as file:
      config = json.load(file)
      return Options(
          client_id=config['google_auth']['client_id'],
          client_secret=config['google_auth']['client_secret'],
          callback_url=config['google_auth']['callback'],
          session_secret=config['session_secret'])


class _AuthBase(pattern.Logger):

  def __init__(self, *args, **kwargs):
    super(_AuthBase, self).__init__(*args, **kwargs)
    self._authorized_tokens = []

  def is_authorized(self, token):
    return token in self._authorized_tokens

  def authorize(self, callback, *args, **kwargs):
    token = self.get_token()
    if not token:
      return self._on_no_token()

    if not self.is_authorized(token):
      if not self._authorize_by_token(token):
        self._on_unauthorized_token()

      self._authorized_tokens.append(token)

    return callback(*args, **kwargs)

  def get_token(self):
    return flask.session.get('access_token')

  def _on_no_token(self):
    flask.abort(401)

  def _authorize_by_token(self, token):
    return False

  def _on_unauthorized_token(self):
    flask.session.pop('access_token', None)
    flask.abort(401)


class Auth(_AuthBase):

  def __init__(self, options, web, auth_callback, *args, **kwargs):
    super(Auth, self).__init__(*args, **kwargs)
    self._callback_url = options.callback_url
    self._auth_callback = auth_callback

    self._oauth = client.OAuth()
    self._google = self._oauth.remote_app(
        'google',
        base_url='https://www.googleapis.com/oauth2/v1/',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        request_token_url=None,
        request_token_params={'scope': 'email'},
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_method='POST',
        consumer_key=options.client_id,
        consumer_secret=options.client_secret)
    self._google.tokengetter(self.get_token)

    self.logger.debug('Configuring authentication for flask...')
    url = urlparse.urlparse(options.callback_url)
    web.secret_key = options.session_secret
    web.add_url_rule('/login', endpoint='login', view_func=self._login)
    web.add_url_rule(url.path, view_func=self._login_callback)
    web.auth = self

  def _login(self):
    flask.session['redirect_url'] = flask.request.url
    return self._google.authorize(callback=self._callback_url)

  def _login_callback(self):
    resp = self._google.authorized_response()
    token = resp['access_token']
    flask.session['access_token'] = token

    redirect_url = flask.session['redirect_url']
    print 'Redirect:' + redirect_url
    if redirect_url:
      return flask.redirect(redirect_url)
    else:
      return flask.redirect(flask.url_for('index'))

  def _on_no_token(self):
    return self._login()

  def _authorize_by_token(self, token):
    user = self._google.get(url='userinfo', token=(token, '')).data
    return user and self._auth_callback(user['email'])
