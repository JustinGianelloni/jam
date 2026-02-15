from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Address(BaseModel):
    country: str | None = None
    extended_address: str | None = Field(default=None, alias="extendedAddress")
    id: str | None = None
    locality: str | None = None
    po_box: str | None = Field(default=None, alias="poBox")
    postal_code: str | None = Field(default=None, alias="postalCode")
    region: str | None = None
    street_address: str | None = Field(default=None, alias="streetAddress")
    type: str | None = None


class Admin(BaseModel):
    id: str | None = None
    role_name: str | None = Field(default=None, alias="roleName")


class Attribute(BaseModel):
    name: str
    value: str


class DelegatedAuthority(BaseModel):
    id: str
    name: str


class MFA(BaseModel):
    configured: bool
    exclusion: bool
    exclusion_days: int | None = Field(default=None, alias="exclusionDays")
    exclusion_until: datetime | None = Field(
        default=None,
        alias="exclusionUntil",
    )


class MFAEnrollment(BaseModel):
    overall_status: str = Field(alias="overallStatus")
    push_status: str = Field(alias="pushStatus")
    totp_status: str = Field(alias="totpStatus")
    web_authn_status: str = Field(alias="webAuthnStatus")


class PhoneNumber(BaseModel):
    id: str | None = None
    number: str | None = None
    type: str | None = None


class RecoveryEmail(BaseModel):
    address: str | None = None
    verified: bool
    verified_at: datetime | None = Field(default=None, alias="verifiedAt")


class Relationship(BaseModel):
    type: str
    value: str


class RestrictedField(BaseModel):
    field: str | None = None
    id: str | None = None
    type: str | None = None


class SSHKey(BaseModel):
    _id: str
    create_date: str
    name: str
    public_key: str


class State(StrEnum):
    STAGED = "STAGED"
    ACTIVATED = "ACTIVATED"
    SUSPENDED = "SUSPENDED"


class User(BaseModel):
    id: str = Field(alias="_id")
    account_locked: bool
    account_locked_date: str | None = None
    activated: bool
    addresses: list[Address] | None = None
    admin: Admin | None = None
    allow_public_key: bool
    alternate_email: str | None = Field(default=None, alias="alternateEmail")
    attribute: list[Attribute] | None = None
    bad_login_attempts: int | None = Field(
        default=None,
        alias="badLoginAttempts",
    )
    company: str | None = None
    cost_center: str | None = Field(default=None, alias="costCenter")
    created: datetime
    creation_source: str | None = Field(default=None, alias="creationSource")
    delegated_authority: DelegatedAuthority | None = Field(
        default=None,
        alias="delegatedAuthority",
    )
    department: str | None = None
    description: str | None = None
    disable_device_max_login_attempts: bool = Field(
        alias="disableDeviceMaxLoginAttempts",
    )
    display_name: str | None = Field(default=None, alias="displayname")
    email: str
    employee_identifier: str | None = Field(
        default=None,
        alias="employeeIdentifier",
    )
    employee_type: str | None = Field(default=None, alias="employeeType")
    enabled_managed_uid: bool | None = None
    enable_user_portal_multifactor: bool
    external_dn: str | None = None
    external_password_expiration_date: datetime | None = None
    external_source_type: str | None = None
    externally_managed: bool
    first_name: str | None = Field(default=None, alias="firstname")
    job_title: str | None = Field(default=None, alias="jobTitle")
    last_name: str | None = Field(default=None, alias="lastname")
    ldap_binding_user: bool
    location: str | None = None
    managed_apple_id: str | None = Field(default=None, alias="managedAppleId")
    manager: str | None = None
    mfa: MFA
    mfa_enrollment: MFAEnrollment = Field(alias="mfaEnrollment")
    middle_name: str | None = Field(default=None, alias="middlename")
    organization: str | None = None
    password_date: datetime | None = None
    password_expiration_date: datetime | None = None
    password_expired: bool
    password_never_expires: bool
    passwordless_sudo: bool
    phone_numbers: list[PhoneNumber] | None = Field(
        default=None,
        alias="phoneNumbers",
    )
    public_key: str | None = None
    recovery_email: RecoveryEmail | None = Field(
        default=None,
        alias="recoveryEmail",
    )
    relationships: list[Relationship] | None = None
    restricted_fields: list[RestrictedField] | None = Field(
        default=None,
        alias="restrictedFields",
    )
    samba_service_user: bool
    ssh_keys: list[SSHKey] | None = None
    state: State
    sudo: bool
    suspended: bool
    tags: list[str] | None = None
    totp_enabled: bool
    unix_guid: int | None = None
    unix_uid: int | None = None
    username: str | None = None

    @property
    def pretty_state(self) -> str:
        match self.state:
            case State.ACTIVATED:
                return "[green]ACTIVATED[/green]"
            case State.SUSPENDED:
                return "[red]SUSPENDED[/red]"
            case State.STAGED:
                return "[yellow]STAGED[/yellow]"
