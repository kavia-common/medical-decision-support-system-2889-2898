from rest_framework.decorators import api_view
from rest_framework.response import Response

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint returning a simple status message."""
    return Response({"message": "Server is up!"})
