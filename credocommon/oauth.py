# -*- coding: utf-8 -*-

import requests

from django.conf import settings


def get_token(code, provider):
    token_endpoint = settings.OAUTH_PROVIDERS[provider]["token_endpoint"]
    client_id = settings.OAUTH_PROVIDERS[provider]["client_id"]
    client_secret = settings.OAUTH_PROVIDERS[provider]["client_secret"]
    redirect_uri = settings.OAUTH_PROVIDERS[provider]["redirect_uri"]

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code": code,
    }

    r = requests.post(token_endpoint, data=payload, timeout=5)
    r.raise_for_status()

    resp = r.json()

    return resp["access_token"], resp["refresh_token"]


def refresh_token(token, provider):
    token_endpoint = settings.OAUTH_PROVIDERS[provider]["token_endpoint"]
    client_id = settings.OAUTH_PROVIDERS[provider]["client_id"]
    client_secret = settings.OAUTH_PROVIDERS[provider]["client_secret"]

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": token,
    }

    r = requests.post(token_endpoint, data=payload, timeout=5)
    r.raise_for_status()

    resp = r.json()

    return resp["access_token"], resp["refresh_token"]


def get_userinfo(token, provider):
    userinfo_endpoint = settings.OAUTH_PROVIDERS[provider]["userinfo_endpoint"]

    r = requests.get(
        userinfo_endpoint,
        headers={"Authorization": "Bearer " + token},
        timeout=5,
    )
    r.raise_for_status()

    resp = r.json()

    email = resp["email"]
    username = resp["preferred_username"]
    display_name = resp["nickname"]

    return email, username, display_name
