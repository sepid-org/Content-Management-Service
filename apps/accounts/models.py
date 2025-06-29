import uuid
from datetime import datetime, timedelta

import pytz
from django.db.models import Index
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel

from apps.accounts.utils.password import make_random_password
from apps.sale.validators import percentage_validator
from content_management_service.settings.base import (
    DISCOUNT_CODE_LENGTH,
    PURCHASE_UNIQ_CODE_LENGTH,
    VOUCHER_CODE_LENGTH,
)
from proxies.sms_system.settings import SMS_CODE_DELAY, SMS_CODE_LENGTH
from proxies.sms_system.sms_service_proxy import SMSServiceProxy


class User(AbstractUser):
    class Gender(models.TextChoices):
        Male = "Male"
        Female = "Female"

    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, unique=True
    )
    # national code should not be unique, due it's not validated
    national_code = models.CharField(max_length=10, null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, max_length=2000)
    bio = models.CharField(max_length=300, blank=True, null=True)
    gender = models.CharField(
        max_length=10, null=True, blank=True, choices=Gender.choices
    )
    birth_date = models.DateField(null=True, blank=True)

    country = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    is_temporary = models.BooleanField(default=False)
    origin = models.CharField(max_length=50, blank=True, null=True)

    def get_user_website(self, website):
        try:
            return self.user_websites.get(website=website.name)
        except:
            return None

    def get_receipt(self, form):
        from apps.fsm.models import RegistrationReceipt

        try:
            return RegistrationReceipt.objects.get(user=self, form=form)
        except:
            return None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            Index(fields=["username"]),
            Index(fields=["email"]),
            Index(fields=["phone_number"]),
        ]


class UserWebsite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="user_websites"
    )
    website = models.CharField(max_length=50)
    password = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def set_password(self, new_password):
        from django.contrib.auth.hashers import make_password

        self.password = make_password(new_password)
        self.save()

    class Meta:
        unique_together = ("user", "website")

    def __str__(self):
        return f"{self.user} | {self.website}"


class UserWebsiteLogin(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    user_website = models.ForeignKey(to=UserWebsite, on_delete=models.CASCADE)


class InstituteManager(PolymorphicManager):
    @transaction.atomic
    def create(self, **args):
        institute = super().create(**args)
        institute.owner = institute.creator
        institute.admins.add(institute.creator)
        # ct = ContentType.objects.get_for_model(institute)
        # assign_perm(Permission.objects.filter(codename='add_admin', content_type=ct).first(), institute.owner, institute)
        # these permission settings worked correctly but were too messy
        institute.save()
        return institute


class EducationalInstitute(PolymorphicModel):
    class InstituteType(models.TextChoices):
        School = "School"
        University = "University"
        Other = "Other"

    name = models.CharField(max_length=100, null=False, blank=False)
    institute_type = models.CharField(
        max_length=10, null=False, blank=False, choices=InstituteType.choices
    )
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    contact_info = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)

    is_approved = models.BooleanField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(
        User,
        related_name="owned_institutes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    admins = models.ManyToManyField(
        User, related_name="institutes", blank=True)

    objects = InstituteManager()

    class Meta:
        permissions = [
            ("add_admin", "Can add new admins to educational institute")
        ]

    def __str__(self):
        return self.name


class School(EducationalInstitute):
    class Gender(models.TextChoices):
        Male = "Male"
        Female = "Female"

    class SchoolType(models.Choices):
        Elementary = "Elementary"
        JuniorHigh = "JuniorHigh"
        High = "High"
        SchoolOfArt = "SchoolOfArt"

    principal_name = models.CharField(max_length=30, null=True, blank=True)
    principal_phone = models.CharField(max_length=15, null=True, blank=True)
    school_type = models.CharField(
        max_length=15, null=True, blank=True, choices=SchoolType.choices
    )
    gender_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=Gender.choices,
        default="Male",
    )


class University(EducationalInstitute):
    pass


class Studentship(PolymorphicModel):
    class StudentshipType(models.Choices):
        School = "School"
        Academic = "Academic"

    studentship_type = models.CharField(
        max_length=100, null=False, blank=False, choices=StudentshipType.choices)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    document = models.URLField(max_length=2000, null=True)
    is_document_verified = models.BooleanField(default=False)


class SchoolStudentship(Studentship):
    class Major(models.TextChoices):
        Math = "Math"
        Biology = "Biology"
        Literature = "Literature"
        IslamicStudies = "IslamicStudies"
        TechnicalTraining = "TechnicalTraining"
        Others = "Others"

    school = models.ForeignKey(
        School, related_name="students", on_delete=models.SET_NULL, null=True
    )
    grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(12), MinValueValidator(0)],
    )
    major = models.CharField(
        max_length=25, null=True, blank=True, choices=Major.choices
    )
    user = models.OneToOneField(
        User,
        related_name="school_studentship",
        on_delete=models.CASCADE,
        null=False,
    )


class AcademicStudentship(Studentship):
    class Degree(models.TextChoices):
        BA = "BA"
        MA = "MA"
        PHD = "PHD"
        Postdoc = "Postdoc"

    university = models.ForeignKey(
        University,
        related_name="academic_students",
        on_delete=models.SET_NULL,
        null=True,
    )
    degree = models.CharField(
        max_length=15, null=True, blank=True, choices=Degree.choices
    )
    university_major = models.CharField(max_length=30, null=True, blank=True)
    user = models.OneToOneField(
        User,
        related_name="academic_studentship",
        on_delete=models.CASCADE,
        null=False,
    )


# class OwnableMixin(models.Model):
#     owners = models.ManyToManyField(User, related_name='owned_entities')
#
#     # TODO - work on its details
#     class Meta:
#         abstract = True


class Merchandise(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    discounted_price = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    program = models.ForeignKey(
        to="fsm.Program", on_delete=models.CASCADE, related_name="merchandises"
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)


# class Code(models.Model):
#     TODO - create a 'code' class  and subclass discounts, vouchers & verification codes from it.
#     class CodeType(models.TextChoices):
#         DISCOUNT_CODE = 'DISCOUNT_CODE'
#         VOUCHER = 'VOUCHER'
#         VERIFICATION_CODE = 'VERIFICATION_CODE'
#
#     code_type = models.CharField(max_length=15, choices=CodeType.choices, blank=False, null=False)
#     code = models.CharField(max_length=10, null=False, blank=False)


class VerificationCodeManager(models.Manager):
    @transaction.atomic
    def create_verification_code(self, phone_number, time_zone="Asia/Tehran"):
        code = make_random_password(
            length=SMS_CODE_LENGTH, allowed_chars="1234567890"
        )
        other_codes = VerificationCode.objects.filter(
            phone_number=phone_number, is_valid=True
        )
        for c in other_codes:
            c.is_valid = False
            c.save()
        verification_code = VerificationCode.objects.create(
            code=code,
            phone_number=phone_number,
            expiration_date=datetime.now(pytz.timezone(time_zone))
            + timedelta(minutes=SMS_CODE_DELAY),
        )
        return verification_code


class VerificationCode(models.Model):
    class VerificationType(models.TextChoices):
        CreateUserAccount = "create-user-account"
        ChangeUserPassword = "change-user-password"
        ChangeUserPhoneNumber = "change-user-phone-number"

    # todo: set verification code while sending verification code
    verification_type = models.CharField(
        blank=False, null=True, choices=VerificationType.choices, max_length=30
    )
    phone_number = models.CharField(blank=True, max_length=13, null=True)
    code = models.CharField(blank=True, max_length=10, null=True)
    expiration_date = models.DateTimeField(blank=False, null=False)
    is_valid = models.BooleanField(default=True)

    objects = VerificationCodeManager()

    def notify(self, verification_type, website_display_name="سپید"):
        sms_service_proxy = SMSServiceProxy(provider="kavenegar")
        sms_service_proxy.send_otp(
            receptor_phone_number=self.phone_number,
            action=verification_type,
            token=website_display_name,
            token2=str(self.code),
        )

    def __str__(self):
        return f'{self.phone_number}\'s code is: {self.code} {"+" if self.is_valid else "-"}'


########### SALE APP ###########

class DiscountCodeManager(models.Manager):
    @transaction.atomic
    def create_unique(self, **attrs):
        import string
        from django.utils.crypto import get_random_string

        length = DISCOUNT_CODE_LENGTH
        chars = string.ascii_letters + string.digits

        while True:
            code = get_random_string(length, allowed_chars=chars)
            if not self.filter(code=code).exists():
                break

        merchandises = attrs.pop('merchandises', None)

        attrs['code'] = code
        instance = super().create(**attrs)

        if merchandises:
            instance.merchandises.set(merchandises)

        return instance


def round_to_hundred(amount: float) -> int:
    """Round `amount` to the nearest 100 units."""
    return int((amount + 50) // 100) * 100


class DiscountCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    value = models.FloatField(validators=[percentage_validator])
    expiration_date = models.DateTimeField(blank=True, null=True)
    remaining = models.PositiveIntegerField(
        null=True, blank=True, default=None,
        help_text="NULL means unlimited uses"
    )
    user = models.ForeignKey(
        User,
        related_name="discount_codes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    merchandises = models.ManyToManyField(
        to=Merchandise, related_name="discount_codes"
    )
    max_discount_amount = models.IntegerField(null=True, blank=True)
    objects = DiscountCodeManager()

    def __str__(self):
        return f"{self.code} ({self.value:.0%})"

    def calculate_discounted_price(self, price: float) -> int:
        discounted = round_to_hundred(price * (1 - self.value))
        if self.max_discount_amount:
            cap_price = price - self.max_discount_amount
            return max(discounted, cap_price)
        return discounted

    def apply(self, merchandise) -> int:
        initial_price = merchandise.discounted_price if merchandise.discounted_price else merchandise.price
        new_price = self.calculate_discounted_price(initial_price)
        if self.remaining:
            self.remaining -= 1
            self.save()
        return new_price

    def revert_apply(self):
        if self.remaining:
            self.remaining += 1
            self.save()


class PurchaseManager(models.Manager):
    @transaction.atomic
    def create_purchase(self, **args):
        uniq_code = make_random_password(length=PURCHASE_UNIQ_CODE_LENGTH)
        return super(PurchaseManager, self).create(
            **{"uniq_code": uniq_code, **args}
        )


class Purchase(models.Model):
    class Status(models.TextChoices):
        Success = "Success"
        Repetitious = "Repetitious"
        Failed = "Failed"
        Started = "Started"

    ref_id = models.CharField(blank=True, max_length=100, null=True)
    amount = models.IntegerField()
    authority = models.CharField(blank=True, max_length=37, null=True)
    status = models.CharField(
        blank=False,
        default=Status.Started,
        choices=Status.choices,
        max_length=25,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    uniq_code = models.CharField(blank=False, max_length=100, default="")
    callback_domain = models.CharField(blank=True, null=True, max_length=100)
    user = models.ForeignKey(
        User,
        related_name="purchases",
        on_delete=models.CASCADE,
    )
    merchandise = models.ForeignKey(
        Merchandise,
        related_name="purchases",
        on_delete=models.PROTECT,
    )
    discount_code = models.ForeignKey(
        DiscountCode,
        related_name="purchases",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = PurchaseManager()

    @property
    def registration_receipt(self):
        return self.merchandise.program.registration_form.registration_receipts.filter(
            user=self.user
        ).last()

    def __str__(self):
        return f"{self.uniq_code}-{self.merchandise}-{self.amount}-{self.status}"
