ADMIN_EMAILS = [
    "anwar.mounir@centrale-casablanca.ma",
    "yahya.elomari@centrale-casablanca.ma",
    "ahmadmoubarak.tiemtore@centrale-casablanca.ma",
    "yahya.barhoun@centrale-casablanca.ma",
    "meryem.soussi@centrale-casablanca.ma",
]

def is_admin(email):
    """Check if the given email has admin privileges."""
    if not email:
        return False
    return email.lower() in [e.lower() for e in ADMIN_EMAILS]
