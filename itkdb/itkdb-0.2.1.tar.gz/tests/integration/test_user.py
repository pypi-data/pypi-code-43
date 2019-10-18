import itkdb
import logging
import betamax

# because expiration will fail (since we cache this information) skip the verification of expiration
jwtOptions = {'verify_signature': False, 'verify_iat': False, 'verify_exp': False}


def test_user_create():
    user = itkdb.core.User(accessCode1='foo', accessCode2='bar')
    assert user.access_token is None
    assert user.bearer == ''
    assert user.id_token == {}
    assert user.name == ''
    assert user.expires_at == 0
    assert user.expires_in == 0
    assert user.is_anonymous() == False
    assert user.is_expired()


# NB: because we are using betamax - the ID token which is invalid after 2
# hours is kept so user.is_expired() will be true for testing, do not assert it
def test_user_anonymous_login(caplog):
    user = itkdb.core.User(accessCode1='', accessCode2='', jwtOptions=jwtOptions)
    with betamax.Betamax(user._session).use_cassette(
        'test_user.test_user_anonymous_login'
    ):
        with caplog.at_level(logging.INFO, 'itkdb'):
            user.authenticate()
            assert "You've logged in as an anonymous user" in caplog.text
        assert user.is_anonymous()
        assert user.is_authenticated()
        assert user._response


# NB: because we are using betamax - the ID token which is invalid after 2
# hours is kept so user.is_expired() will be true for testing, do not assert it
def test_user_anonymous_login_saved(tmpdir, mocker, caplog):
    temp = tmpdir.join("auth.pkl")
    user = itkdb.core.User(
        save_auth=temp.strpath, accessCode1='', accessCode2='', jwtOptions=jwtOptions
    )
    mocker.patch(
        'itkdb.core.User.is_expired', return_value=False, wraps=user.is_expired
    )
    with betamax.Betamax(user._session).use_cassette(
        'test_user.test_user_anonymous_login'
    ):
        user.authenticate()
        assert temp.isfile()
        assert user.is_anonymous()
        assert user.is_authenticated()
        assert user._response
        caplog.clear()

        with caplog.at_level(logging.INFO, 'itkdb'):
            user = itkdb.core.User(
                save_auth=temp.strpath,
                accessCode1='',
                accessCode2='',
                jwtOptions=jwtOptions,
            )
            assert 'Saved user session is anonymous in' in caplog.text


def test_user_bad_login(caplog):
    user = itkdb.core.User(accessCode1='foo', accessCode2='bar', jwtOptions=jwtOptions)
    with betamax.Betamax(user._session).use_cassette('test_user.test_user_bad_login'):
        with caplog.at_level(logging.INFO, 'itkdb'):
            user.authenticate()
            assert (
                'Authorization failed. Unable to authenticate Account, user is not registered or invalid credentials used for realm \'users.realm.uu\'!'
                in caplog.text
            )
        assert user.is_anonymous() == False
        assert user.is_authenticated() == False
        assert user._response


# NB: because we are using betamax - the ID token which is invalid after 2
# hours is kept so user.is_expired() will be true for testing, do not assert it
def test_user_good_login(caplog):
    user = itkdb.core.User(jwtOptions=jwtOptions)
    with betamax.Betamax(user._session).use_cassette('test_user.test_user_good_login'):
        with caplog.at_level(logging.INFO, 'itkdb'):
            user.authenticate()
            assert caplog.text == ''
        assert user.is_anonymous() == False
        assert user.is_authenticated()
        assert user._response
