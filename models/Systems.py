from datetime import datetime

from pydantic import BaseModel, Field


class Attribute(BaseModel):
    name: str
    value: str


class BuiltInCommands(BaseModel):
    name: str
    type: str


class DomainInfo(BaseModel):
    domain_name: str = Field(alias="domainName")
    part_of_domain: bool = Field(alias="partOfDomain")


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
    dep: bool
    enrollment_type: str | None = Field(default=None, alias="enrollmentType")
    internal: Internal | None = None
    lost_mode_status: str | None = Field(default=None, alias="lostModeStatus")
    profile_identifier: str | None = Field(
        default=None, alias="profileIdentifier"
    )
    provider_id: str | None = Field(default=None, alias="profileId")
    userApproved: bool = Field(alias="userApproved")
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
    id: str


class Provisioner(BaseModel):
    provisionerId: str
    type: str


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
    _id: str
    active: bool
    agent_has_full_disk_access: bool = Field(alias="agentHasFullDiskAccess")
    agent_version: str | None = Field(default=None, alias="agentVersion")
    allow_multifactor_authentication: bool = Field(
        alias="allowMultiFactorAuthentication"
    )
    allow_public_key_authentication: bool = Field(
        alias="allowPublicKeyAuthentication"
    )
    allow_ssh_password_authentication: bool = Field(
        alias="allowSshPasswordAuthentication"
    )
    allow_ssh_root_login: bool = Field(alias="allowSshRootLogin")
    amazon_instance_id: str | None = Field(
        default=None, alias="amazonInstanceID"
    )
    arch: str | None = None
    arch_family: str | None = Field(default=None, alias="archFamily")
    attributes: list[Attribute] | None = None
    azure_ad_joined: bool = Field(alias="azureAdJoined")
    built_in_commands: list[BuiltInCommands] | None = Field(
        default=None, alias="builtInCommands"
    )
    connection_history: list[str] | None = Field(
        default=None, alias="connectionHistory"
    )
    created: datetime
    description: str | None = None
    desktop_capable: bool = Field(alias="desktopCapable")
    display_manager: str | None = Field(default=None, alias="displayManager")
    display_name: str | None = Field(default=None, alias="displayName")
    domain_info: DomainInfo | None = Field(default=None, alias="domainInfo")
    fde: FDE | None = None
    file_system: str | None = Field(default=None, alias="fileSystem")
    has_service_account: bool = Field(alias="hasServiceAccount")
    hostname: str | None = None
    hw_vendor: str | None = Field(default=None, alias="hwVendor")
    is_policy_bound: bool = Field(alias="isPolicyBound")
    last_contact: datetime | None = Field(default=None, alias="lastContact")
    mdm: MDM | None = None
    modify_sshd_config: bool = Field(alias="modifySSHDConfig")
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
    ssh_root_enabled: bool = Field(alias="sshRootEnabled")
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
