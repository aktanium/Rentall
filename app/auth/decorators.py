from functools import wraps

from flask import abort
from flask_login import current_user

from app.extensions import login_manager


def _require(flag: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if not getattr(current_user, flag):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


owner_required = _require("is_owner")
owner_required.__doc__ = "Allow only owners; anonymous users go to login, others get 403."

admin_required = _require("is_admin")
admin_required.__doc__ = "Allow only admins; anonymous users go to login, others get 403."
