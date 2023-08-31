from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer


@api_view(['POST'])
def identify_contact(request):
    email = request.data.get('email')
    phoneNumber = request.data.get('phoneNumber')

    if not email and not phoneNumber:
        return Response({'error': 'Email or phoneNumber is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a contact already exists with the provided email or phoneNumber
    existing_contact = None
    if email:
        existing_contact = Contact.objects.filter(email=email).first()
    if not existing_contact and phoneNumber:
        existing_contact = Contact.objects.filter(phoneNumber=phoneNumber).first()

    if existing_contact:
        # Create a secondary contact
        contact_data = {
            'email': email,
            'phoneNumber': phoneNumber,
            'linkedId': existing_contact if existing_contact.linkPrecedence == 'primary' else existing_contact.linkedId,
            'linkPrecedence': 'secondary',
        }
        contact_serializer = ContactSerializer(data=contact_data)
        if contact_serializer.is_valid():
            contact_serializer.save()
        else:
            return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Return the consolidated contact
        consolidated_contact = {
            'primaryContactId': existing_contact.id,
            'emails': [existing_contact.email] if existing_contact.email else [],
            'phoneNumbers': [existing_contact.phoneNumber] if existing_contact.phoneNumber else [],
            'secondaryContactIds': Contact.objects.filter(linkedId=existing_contact).values_list('id', flat=True),
        }
        return Response({'contact': consolidated_contact}, status=status.HTTP_200_OK)

    else:
        # Create a new primary contact
        contact_data = {
            'email': email,
            'phoneNumber': phoneNumber,
            'linkPrecedence': 'primary',
        }
        contact_serializer = ContactSerializer(data=contact_data)
        if contact_serializer.is_valid():
            contact_serializer.save()
            return Response({'contact': {'primaryContactId': contact_serializer.data['id'], 'emails': [], 'phoneNumbers': [], 'secondaryContactIds': []}}, status=status.HTTP_200_OK)
        else:
            return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
