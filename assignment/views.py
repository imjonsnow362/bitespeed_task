from django.db.models import Q
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

    existing_contacts = Contact.objects.filter(Q(email=email) | Q(phoneNumber=phoneNumber))

    if existing_contacts.exists():
        primary_contact = existing_contacts.filter(linkPrecedence='primary').first()

        if primary_contact:
            if (email and primary_contact.email != email) or (phoneNumber and primary_contact.phoneNumber != phoneNumber):

                contact_data = {
                    'email': email,
                    'phoneNumber': phoneNumber,
                    'linkedId': primary_contact.id,
                    'linkPrecedence': 'secondary',
                }
                contact_serializer = ContactSerializer(data=contact_data)
                if contact_serializer.is_valid():
                    secondary_contact = contact_serializer.save()


                    secondary_contacts = existing_contacts.filter(linkPrecedence='secondary')
                    emails = [primary_contact.email] + [contact.email for contact in secondary_contacts]
                    phone_numbers = [primary_contact.phoneNumber] + [contact.phoneNumber for contact in secondary_contacts]
                    secondary_contact_ids = [contact.id for contact in secondary_contacts] + [secondary_contact.id]

                    consolidated_contact = {
                        'primaryContactId': primary_contact.id,
                        'emails': emails,
                        'phoneNumbers': phone_numbers,
                        'secondaryContactIds': secondary_contact_ids,
                    }
                    return Response({'contact': consolidated_contact}, status=status.HTTP_200_OK)
                else:
                    return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:

                consolidated_contact = {
                    'primaryContactId': primary_contact.id,
                    'emails': [primary_contact.email],
                    'phoneNumbers': [primary_contact.phoneNumber],
                    'secondaryContactIds': [],
                }
                return Response({'contact': consolidated_contact}, status=status.HTTP_200_OK)

    #Comment
    contact_data = {
        'email': email,
        'phoneNumber': phoneNumber,
        'linkPrecedence': 'primary',
    }
    contact_serializer = ContactSerializer(data=contact_data)
    if contact_serializer.is_valid():
        primary_contact = contact_serializer.save()
        return Response({'contact': {'primaryContactId': primary_contact.id, 'emails': [primary_contact.email], 'phoneNumbers': [primary_contact.phoneNumber], 'secondaryContactIds': []}}, status=status.HTTP_200_OK)
    else:
        return Response(contact_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

