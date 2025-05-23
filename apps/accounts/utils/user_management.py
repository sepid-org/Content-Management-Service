from django.db.models import Q
from rest_framework.exceptions import ParseError
from django.contrib.auth.hashers import make_password, check_password

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.models import User, UserWebsite
from apps.accounts.serializers.custom_token_obtain import CustomTokenObtainSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import RegistrationForm, RegistrationReceipt, Team, AnswerSheet
from apps.fsm.serializers.answer_sheet_serializers import MinimalRegistrationReceiptSerializer


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = CustomTokenObtainSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.get('access')
    refresh_token = token_data.get('refresh')
    return access_token, refresh_token


def standardize_phone_number(phone_number):
    # todo: convert input phone_number string to standard form
    return phone_number


def find_user(user_data):
    # Get the user data fields
    id = user_data.get('id')
    phone_number = standardize_phone_number(user_data.get('phone_number'))
    email = user_data.get('email')
    username = user_data.get('username')

    # Build query based on the available fields
    query = Q()

    if id:
        query |= Q(id=id)
    if username:
        query |= Q(username=username)
    if phone_number:
        query |= Q(phone_number=phone_number)
        # todo: this line is because of ambiguity in what username is!
        query |= Q(username=phone_number)
    if email:
        query |= Q(email=email)

    try:
        return User.objects.get(query)
    except User.DoesNotExist:
        return None


def find_user_in_website(user_data, website, raise_exception=False):
    if not website:
        raise ParseError(serialize_error('4116'))

    user = find_user(user_data=user_data)

    if user and user.get_user_website(website=website):
        return user
    else:
        if raise_exception:
            raise ParseError(serialize_error('4115'))
        return None


def create_or_get_user(user_data, website):
    user = find_user(user_data=user_data)
    has_user_website = bool(user and user.get_user_website(website=website))

    if user and has_user_website:
        return user, False

    if not user:
        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

    if not has_user_website:
        UserWebsite.objects.create(
            user=user,
            password=make_password(user_data.get(
                "password")) if user_data.get("password") else None,
            website=website.name,
        )

    # send greeting email
    # if user.email:
    #     email_service_proxy = EmailServiceProxy(website=website)
    #     email_service_proxy.send_greeting_email(
    #         email=user.email,
    #         name=user.full_name,
    #     )

    # send greeting notification
    # notification_service_proxy = InstantMessagingServiceProxy(website=website)
    # notification_service_proxy.send_greeting_notification(recipient=user)

    return user, True


def can_user_login(user, password, website):
    user_website = user.get_user_website(website=website)
    if not user_website.password:
        return False
    if user_website:
        return check_password(password, user_website.password)
    else:
        return False


def find_registration_receipt(user, registration_form):
    return RegistrationReceipt.objects.filter(user=user, form=registration_form).first()


def update_or_create_registration_receipt(user: User, registration_form: RegistrationForm):
    serializer = MinimalRegistrationReceiptSerializer(data={
        'form': registration_form.id,
        'answer_sheet_type': AnswerSheet.AnswerSheetType.RegistrationReceipt,
        'user': user.id,
        'status': RegistrationReceipt.RegistrationStatus.Accepted,
        'is_participating': True,
    })
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    receipt = RegistrationReceipt.objects.filter(
        user=user, form=registration_form).first()
    if receipt:
        return serializer.update(receipt, validated_data)
    else:
        return serializer.save()


def update_or_create_team(participant_group_name: str, chat_room_link: str, receipt: RegistrationReceipt, registration_form: RegistrationForm):
    if not participant_group_name:
        return
    participant_group = create_team(team_name=participant_group_name,
                                    registration_form=registration_form)
    team_with_same_head = Team.objects.filter(
        team_head=receipt).first()
    if team_with_same_head:
        team_with_same_head.team_head = None
        team_with_same_head.save()
    if not participant_group.team_head:
        participant_group.team_head = receipt
    if chat_room_link:
        participant_group.chat_room = chat_room_link
    participant_group.save()
    receipt.team = participant_group
    receipt.save()


def create_team(**data):
    team_name = data.get('team_name', None)
    registration_form = data.get('registration_form', None)

    if not team_name or not registration_form:
        raise ParseError(serialize_error('4113'))
    team = Team.objects.filter(
        name=team_name, registration_form=registration_form).first()
    if not team:
        team = Team.objects.create(
            registration_form=registration_form)
        team.name = team_name
        team.save()

    return team
