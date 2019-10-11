from .services import get_contact_information


def contact_information(request):
    return {
        'contact_information': get_contact_information(),
    }
