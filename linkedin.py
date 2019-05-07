import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.linkedin import make_linkedin_blueprint, linkedin

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["LINKEDIN_OAUTH_CLIENT_ID"] = os.environ.get("LINKEDIN_OAUTH_CLIENT_ID")
app.config["LINKEDIN_OAUTH_CLIENT_SECRET"] = os.environ.get(
    "LINKEDIN_OAUTH_CLIENT_SECRET"
)
linkedin_bp = make_linkedin_blueprint(scope=["r_liteprofile"])
app.register_blueprint(linkedin_bp, url_prefix="/login")


def preferred_locale_value(multi_locale_string):
    """
    Extract the value of the preferred locale from a MultiLocaleString

    https://docs.microsoft.com/en-us/linkedin/shared/references/v2/object-types#multilocalestring
    """
    preferred = multi_locale_string["preferredLocale"]
    locale = "{language}_{country}".format(
        language=preferred["language"], country=preferred["country"]
    )
    return multi_locale_string["localized"][locale]


@app.route("/")
def index():
    if not linkedin.authorized:
        return redirect(url_for("linkedin.login"))
    resp = linkedin.get("me")
    assert resp.ok
    data = resp.json()
    name = "{first} {last}".format(
        first=preferred_locale_value(data["firstName"]),
        last=preferred_locale_value(data["lastName"]),
    )
    return "You are {name} on LinkedIn".format(name=name)
