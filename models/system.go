package models

import "time"

type SystemAttribute struct {
	Name  string `json:"name,omitempty"`
	Value string `json:"value,omitempty"`
}

type SystemBuiltInCommand struct {
	Name string `json:"name,omitempty"` // enum: erase, lock, restart, shutdown
	Type string `json:"type,omitempty"` // enum: security
}

type SystemDomainInfo struct {
	DomainName   string `json:"domainName,omitempty"`
	PartOfDomain bool   `json:"partOfDomain,omitempty"`
}

type SystemFDE struct {
	Active     bool `json:"active,omitempty"`
	KeyPresent bool `json:"keyPresent,omitempty"`
}

type SystemMDMInternal struct {
	DeviceID        string `json:"deviceId,omitempty"`
	WindowsDeviceID string `json:"windowsDeviceId,omitempty"`
}

type SystemMDMWindows struct {
	UPN string `json:"upn,omitempty"`
}

type SystemMDM struct {
	DEP               bool               `json:"dep,omitempty"`
	EnrollmentType    string             `json:"enrollmentType,omitempty"` // enum: unknown, automated device, device, user
	Internal          *SystemMDMInternal `json:"internal,omitempty"`
	LostModeStatus    string             `json:"lostModeStatus,omitempty"`
	ProfileIdentifier string             `json:"profileIdentifier,omitempty"`
	ProviderID        string             `json:"providerId,omitempty"`
	UserApproved      bool               `json:"userApproved,omitempty"`
	Vendor            string             `json:"vendor,omitempty"` // enum: unknown, none, internal, external
	Windows           *SystemMDMWindows  `json:"windows,omitempty"`
}

type SystemNetworkInterface struct {
	Address  string `json:"address,omitempty"`
	Family   string `json:"family,omitempty"` // enum: IPv4, IPv6
	Internal bool   `json:"internal,omitempty"`
	Name     string `json:"name,omitempty"`
}

type SystemOSVersionDetail struct {
	DistributionName string `json:"distributionName,omitempty"`
	Major            string `json:"major,omitempty"`
	MajorNumber      int    `json:"majorNumber,omitempty"`
	Minor            string `json:"minor,omitempty"`
	MinorNumber      int    `json:"minorNumber,omitempty"`
	OSName           string `json:"osName,omitempty"`
	Patch            string `json:"patch,omitempty"`
	PatchNumber      int    `json:"patchNumber,omitempty"`
	ReleaseName      string `json:"releaseName,omitempty"`
	Revision         string `json:"revision,omitempty"`
	Version          string `json:"version,omitempty"`
}

type SystemPolicyStats struct {
	Duplicate     string `json:"duplicate,omitempty"`
	Failed        string `json:"failed,omitempty"`
	Pending       string `json:"pending,omitempty"`
	Success       string `json:"success,omitempty"`
	Total         string `json:"total,omitempty"`
	UnsupportedOS string `json:"unsupportedOs,omitempty"`
}

type SystemPrimaryUser struct {
	ID *string `json:"id,omitempty"`
}

type SystemProvisioner struct {
	ProvisionerID string `json:"provisionerId,omitempty"`
	Type          string `json:"type,omitempty"` // enum: administrator, mdm, user
}

type SystemProvisionMetadata struct {
	Provisioner *SystemProvisioner `json:"provisioner,omitempty"`
}

type SystemSecureLogin struct {
	Enabled   bool `json:"enabled,omitempty"`
	Supported bool `json:"supported,omitempty"`
}

type SystemServiceAccountState struct {
	HasSecureToken    bool `json:"hasSecureToken,omitempty"`
	PasswordAPFSValid bool `json:"passwordAPFSValid,omitempty"`
	PasswordODValid   bool `json:"passwordODValid,omitempty"`
}

type SystemSSHDParam struct {
	Name  string `json:"name,omitempty"`
	Value string `json:"value,omitempty"`
}

type SystemInsights struct {
	State string `json:"state,omitempty"` // enum: enabled, disabled, deferred
}

type SystemUserMetric struct {
	Admin              bool   `json:"admin,omitempty"`
	Managed            bool   `json:"managed,omitempty"`
	SecureTokenEnabled bool   `json:"secureTokenEnabled,omitempty"`
	Suspended          bool   `json:"suspended,omitempty"`
	UserName           string `json:"userName,omitempty"`
}

type System struct {
	ID                             string                     `json:"_id,omitempty"`
	Active                         bool                       `json:"active,omitempty"`
	AgentHasFullDiskAccess         bool                       `json:"agentHasFullDiskAccess,omitempty"`
	AgentVersion                   string                     `json:"agentVersion,omitempty"`
	AllowMultiFactorAuthentication bool                       `json:"allowMultiFactorAuthentication,omitempty"`
	AllowPublicKeyAuthentication   bool                       `json:"allowPublicKeyAuthentication,omitempty"`
	AllowSSHPasswordAuthentication bool                       `json:"allowSshPasswordAuthentication,omitempty"`
	AllowSSHRootLogin              bool                       `json:"allowSshRootLogin,omitempty"`
	AmazonInstanceID               string                     `json:"amazonInstanceID,omitempty"`
	Arch                           string                     `json:"arch,omitempty"`
	ArchFamily                     string                     `json:"archFamily,omitempty"`
	Attributes                     []SystemAttribute          `json:"attributes,omitempty"`
	AzureADJoined                  bool                       `json:"azureAdJoined,omitempty"`
	BuiltInCommands                []SystemBuiltInCommand     `json:"builtInCommands,omitempty"`
	ConnectionHistory              []any                      `json:"connectionHistory,omitempty"`
	Created                        string                     `json:"created,omitempty"`
	Description                    string                     `json:"description,omitempty"`
	DesktopCapable                 bool                       `json:"desktopCapable,omitempty"`
	DisplayManager                 string                     `json:"displayManager,omitempty"`
	DisplayName                    string                     `json:"displayName,omitempty"`
	DomainInfo                     *SystemDomainInfo          `json:"domainInfo,omitempty"`
	FDE                            *SystemFDE                 `json:"fde,omitempty"`
	FileSystem                     *string                    `json:"fileSystem,omitempty"`
	HasServiceAccount              bool                       `json:"hasServiceAccount,omitempty"`
	Hostname                       string                     `json:"hostname,omitempty"`
	HWVendor                       string                     `json:"hwVendor,omitempty"`
	IsPolicyBound                  bool                       `json:"isPolicyBound,omitempty"`
	LastContact                    *time.Time                 `json:"lastContact,omitempty"`
	MDM                            *SystemMDM                 `json:"mdm,omitempty"`
	ModifySSHDConfig               bool                       `json:"modifySSHDConfig,omitempty"`
	NetworkInterfaces              []SystemNetworkInterface   `json:"networkInterfaces,omitempty"`
	Organization                   string                     `json:"organization,omitempty"`
	OS                             string                     `json:"os,omitempty"`
	OSFamily                       string                     `json:"osFamily,omitempty"`
	OSVersionDetail                *SystemOSVersionDetail     `json:"osVersionDetail,omitempty"`
	PolicyStats                    *SystemPolicyStats         `json:"policyStats,omitempty"`
	PrimarySystemUser              *SystemPrimaryUser         `json:"primarySystemUser,omitempty"`
	ProvisionMetadata              *SystemProvisionMetadata   `json:"provisionMetadata,omitempty"`
	RemoteAssistAgentVersion       string                     `json:"remoteAssistAgentVersion,omitempty"`
	RemoteIP                       string                     `json:"remoteIP,omitempty"`
	SecureLogin                    *SystemSecureLogin         `json:"secureLogin,omitempty"`
	SerialNumber                   string                     `json:"serialNumber,omitempty"`
	ServiceAccountState            *SystemServiceAccountState `json:"serviceAccountState,omitempty"`
	SSHRootEnabled                 bool                       `json:"sshRootEnabled,omitempty"`
	SSHDParams                     []SystemSSHDParam          `json:"sshdParams,omitempty"`
	SystemInsights                 *SystemInsights            `json:"systemInsights,omitempty"`
	SystemTimezone                 int                        `json:"systemTimezone,omitempty"`
	Tags                           []string                   `json:"tags,omitempty"`
	TemplateName                   string                     `json:"templateName,omitempty"`
	UserMetrics                    []SystemUserMetric         `json:"userMetrics,omitempty"`
	Version                        string                     `json:"version,omitempty"`
}
