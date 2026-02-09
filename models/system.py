from datetime import datetime

import pytz
from pydantic import BaseModel, Field, field_validator

from core.settings import Settings

SETTINGS = Settings()


class Attribute(BaseModel):
    name: str
    value: str


class BuiltInCommands(BaseModel):
    name: str
    type: str


class DomainInfo(BaseModel):
    domain_name: str | None = Field(default=None, alias="domainName")
    part_of_domain: bool | None = Field(default=None, alias="partOfDomain")


class FDE(BaseModel):
    active: bool
    key_present: bool = Field(alias="keyPresent")


class Internal(BaseModel):
    device_id: str | None = Field(default=None, alias="deviceId")
    windows_device_id: str | None = Field(
        default=None, alias="windowsDeviceId"
    )


class Windows(BaseModel):
    upn: str


class MDM(BaseModel):
    dep: bool | None = None
    enrollment_type: str | None = Field(default=None, alias="enrollmentType")
    internal: Internal | None = None
    lost_mode_status: str | None = Field(default=None, alias="lostModeStatus")
    profile_identifier: str | None = Field(
        default=None, alias="profileIdentifier"
    )
    provider_id: str | None = Field(default=None, alias="profileId")
    userApproved: bool | None = Field(default=None, alias="userApproved")
    vendor: str | None = None
    windows: Windows | None = None


class NetworkInterface(BaseModel):
    address: str | None
    family: str | None
    internal: bool
    name: str | None


class OSVersionDetail(BaseModel):
    distribution_name: str | None = Field(
        default=None, alias="distributionName"
    )
    major: str | None = None
    major_number: int | None = Field(default=None, alias="majorNumber")
    minor: str | None = None
    minor_number: int | None = Field(default=None, alias="minorNumber")
    os_name: str | None = Field(default=None, alias="osName")
    patch: str | None = None
    patch_number: int | None = Field(default=None, alias="patchNumber")
    release_name: str | None = Field(default=None, alias="releaseName")
    revision: str | None = None
    version: str | None = None


class PolicyStats(BaseModel):
    duplicate: int
    failed: int
    pending: int
    success: int
    total: int
    unsupported_os: int = Field(alias="unsupportedOs")


class PrimarySystemUser(BaseModel):
    id: str | None = None


class Provisioner(BaseModel):
    provisioner_id: str | None = Field(default=None, alias="provisionerId")
    type: str | None = None


class ProvisionMetadata(BaseModel):
    provisioner: Provisioner


class SecureLogin(BaseModel):
    enabled: bool
    supported: bool


class ServiceAccountState(BaseModel):
    has_secure_token: bool = Field(alias="hasSecureToken")
    password_APFS_valid: bool = Field(alias="passwordAPFSValid")
    password_od_valid: bool = Field(alias="passwordODValid")


class SSHDParam(BaseModel):
    name: str
    value: str


class SystemInsights(BaseModel):
    state: str


class UserMetric(BaseModel):
    admin: bool
    managed: bool
    secure_token_enabled: bool = Field(alias="secureTokenEnabled")
    suspended: bool
    username: str | None = Field(default=None, alias="userName")


class System(BaseModel):
    id: str = Field(alias="_id")
    active: bool | None = None
    agent_has_full_disk_access: bool | None = Field(
        default=None, alias="agentHasFullDiskAccess"
    )
    agent_version: str | None = Field(default=None, alias="agentVersion")
    allow_multifactor_authentication: bool | None = Field(
        default=None, alias="allowMultiFactorAuthentication"
    )
    allow_public_key_authentication: bool | None = Field(
        default=None, alias="allowPublicKeyAuthentication"
    )
    allow_ssh_password_authentication: bool | None = Field(
        default=None, alias="allowSshPasswordAuthentication"
    )
    allow_ssh_root_login: bool | None = Field(
        default=None, alias="allowSshRootLogin"
    )
    amazon_instance_id: str | None = Field(
        default=None, alias="amazonInstanceID"
    )
    arch: str | None = None
    arch_family: str | None = Field(default=None, alias="archFamily")
    attributes: list[Attribute] | None = None
    azure_ad_joined: bool | None = Field(default=None, alias="azureAdJoined")
    built_in_commands: list[BuiltInCommands] | None = Field(
        default=None, alias="builtInCommands"
    )
    connection_history: list[str] | None = Field(
        default=None, alias="connectionHistory"
    )
    created: datetime | None = None
    description: str | None = None
    desktop_capable: bool | None = Field(default=None, alias="desktopCapable")
    display_manager: str | None = Field(default=None, alias="displayManager")
    display_name: str | None = Field(default=None, alias="displayName")
    domain_info: DomainInfo | None = Field(default=None, alias="domainInfo")
    fde: FDE | None = None
    file_system: str | None = Field(default=None, alias="fileSystem")
    has_service_account: bool | None = Field(
        default=None, alias="hasServiceAccount"
    )
    hostname: str | None = None
    hw_vendor: str | None = Field(default=None, alias="hwVendor")
    is_policy_bound: bool | None = Field(default=None, alias="isPolicyBound")
    last_contact: datetime | None = Field(default=None, alias="lastContact")
    mdm: MDM | None = None
    modify_sshd_config: bool | None = Field(
        default=None, alias="modifySSHDConfig"
    )
    network_interfaces: list[NetworkInterface] | None = Field(
        default=None, alias="networkInterfaces"
    )
    organization: str | None = None
    os: str | None = None
    os_family: str | None = Field(default=None, alias="osFamily")
    os_version_detail: OSVersionDetail | None = Field(
        default=None, alias="osVersionDetail"
    )
    policy_stats: PolicyStats | None = Field(default=None, alias="policyStats")
    primary_system_user: PrimarySystemUser | None = Field(
        default=None, alias="primarySystemUser"
    )
    provision_metadata: ProvisionMetadata | None = Field(
        default=None, alias="provisionMetadata"
    )
    remote_assist_agent_version: str | None = Field(
        default=None, alias="remoteAssistAgentVersion"
    )
    remote_ip: str | None = Field(default=None, alias="remoteIP")
    secure_login: SecureLogin | None = Field(default=None, alias="secureLogin")
    serial_number: str | None = Field(default=None, alias="serialNumber")
    service_account_state: ServiceAccountState | None = Field(
        default=None, alias="serviceAccountState"
    )
    ssh_root_enabled: bool | None = Field(default=None, alias="sshRootEnabled")
    sshd_params: list[SSHDParam] | None = Field(
        default=None, alias="sshdParams"
    )
    system_insights: SystemInsights | None = Field(
        default=None, alias="systemInsights"
    )
    system_timezone: int | None = Field(default=None, alias="systemTimezone")
    tags: list[str] | None = None
    template_name: str | None = Field(default=None, alias="templateName")
    user_metrics: list[UserMetric] | None = Field(
        default=None, alias="userMetrics"
    )
    version: str | None = None

    @property
    def pretty_last_contact(self) -> str:
        tz = pytz.timezone(SETTINGS.local_tz)
        if self.last_contact is None:
            return "Never"
        return self.last_contact.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def pretty_os(self) -> str:
        match self.os:
            case "Windows":
                return "[blue]Windows[/blue]"
            case "Mac OS X":
                return "[magenta]Mac OS X[/magenta]"
            case "Ubuntu":
                return "[yellow]Ubuntu[/yellow]"
            case "Android":
                return "[green]Android[/green]"
            case "iOS":
                return "[purple]iOS[/purple]"
            case "iPadOS":
                return "[magenta]iPadOS[/magenta]"
            case _:
                return self.os_family
