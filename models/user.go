package models

type UserAddress struct {
	Country         string `json:"country,omitempty"`
	ExtendedAddress string `json:"extendedAddress,omitempty"`
	ID              string `json:"id,omitempty"`
	Locality        string `json:"locality,omitempty"`
	PoBox           string `json:"poBox,omitempty"`
	PostalCode      string `json:"postalCode,omitempty"`
	Region          string `json:"region,omitempty"`
	StreetAddress   string `json:"streetAddress,omitempty"`
	Type            string `json:"type,omitempty"`
}

type UserPhoneNumber struct {
	ID     string `json:"id,omitempty"`
	Number string `json:"number,omitempty"`
	Type   string `json:"type,omitempty"`
}

type UserAttribute struct {
	Name  string `json:"name,omitempty"`
	Value string `json:"value,omitempty"`
}

type UserAdmin struct {
	ID        string   `json:"id,omitempty"`
	RoleName  string   `json:"roleName,omitempty"`
	RoleNames []string `json:"roleNames,omitempty"`
}

type UserDelegatedAuthority struct {
	ID   string `json:"id,omitempty"`
	Name string `json:"name,omitempty"` // enum: "ActiveDirectory"
}

type UserMFA struct {
	Configured     bool   `json:"configured,omitempty"`
	Exclusion      bool   `json:"exclusion,omitempty"`
	ExclusionDays  int    `json:"exclusionDays,omitempty"`
	ExclusionUntil string `json:"exclusionUntil,omitempty"` // date-time
}

type MFAEnrollmentStatus string

const (
	MFAEnrollmentStatusNotEnrolled       MFAEnrollmentStatus = "NOT_ENROLLED"
	MFAEnrollmentStatusDisabled          MFAEnrollmentStatus = "DISABLED"
	MFAEnrollmentStatusPendingActivation MFAEnrollmentStatus = "PENDING_ACTIVATION"
	MFAEnrollmentStatusEnrollmentExpired MFAEnrollmentStatus = "ENROLLMENT_EXPIRED"
	MFAEnrollmentStatusInEnrollment      MFAEnrollmentStatus = "IN_ENROLLMENT"
	MFAEnrollmentStatusPreEnrollment     MFAEnrollmentStatus = "PRE_ENROLLMENT"
	MFAEnrollmentStatusEnrolled          MFAEnrollmentStatus = "ENROLLED"
)

type UserMFAEnrollment struct {
	JCGoStatus     MFAEnrollmentStatus `json:"jcGoStatus,omitempty"`
	OverallStatus  MFAEnrollmentStatus `json:"overallStatus,omitempty"`
	PushStatus     MFAEnrollmentStatus `json:"pushStatus,omitempty"`
	TotpStatus     MFAEnrollmentStatus `json:"totpStatus,omitempty"`
	WebAuthnStatus MFAEnrollmentStatus `json:"webAuthnStatus,omitempty"`
}

type UserRecoveryEmail struct {
	Address    string `json:"address,omitempty"`
	Verified   bool   `json:"verified,omitempty"`
	VerifiedAt string `json:"verifiedAt,omitempty"`
}

type UserRelationship struct {
	Type  string `json:"type,omitempty"`
	Value string `json:"value,omitempty"`
}

type UserSSHKey struct {
	ID         string `json:"id,omitempty"`
	Name       string `json:"name,omitempty"`
	PublicKey  string `json:"public_key,omitempty"`
	CreateDate string `json:"create_date,omitempty"`
}

type UserState string

const (
	UserStateStaged    UserState = "STAGED"
	UserStateActivated UserState = "ACTIVATED"
	UserStateSuspended UserState = "SUSPENDED"
)

type User struct {
	ID                             string                  `json:"_id,omitempty"`
	AccountLocked                  bool                    `json:"account_locked,omitempty"`
	AccountLockedDate              *string                 `json:"account_locked_date,omitempty"`
	Activated                      bool                    `json:"activated,omitempty"`
	Addresses                      []UserAddress           `json:"addresses,omitempty"`
	Admin                          *UserAdmin              `json:"admin,omitempty"`
	AllowPublicKey                 bool                    `json:"allow_public_key,omitempty"`
	AlternateEmail                 string                  `json:"alternateEmail,omitempty"`
	Attributes                     []UserAttribute         `json:"attributes,omitempty"`
	BadLoginAttempts               int                     `json:"badLoginAttempts,omitempty"`
	Company                        string                  `json:"company,omitempty"`
	CostCenter                     string                  `json:"costCenter,omitempty"`
	Created                        string                  `json:"created,omitempty"`
	CreationSource                 string                  `json:"creationSource,omitempty"`
	DelegatedAuthority             *UserDelegatedAuthority `json:"delegatedAuthority,omitempty"`
	Department                     string                  `json:"department,omitempty"`
	Description                    string                  `json:"description,omitempty"`
	DisableDeviceMaxLoginAttempts  bool                    `json:"disableDeviceMaxLoginAttempts,omitempty"`
	DisplayName                    string                  `json:"displayname,omitempty"`
	Email                          string                  `json:"email,omitempty"`
	EmployeeIdentifier             string                  `json:"employeeIdentifier,omitempty"`
	EmployeeType                   string                  `json:"employeeType,omitempty"`
	EnableManagedUID               bool                    `json:"enable_managed_uid,omitempty"`
	EnableUserPortalMultifactor    bool                    `json:"enable_user_portal_multifactor,omitempty"`
	ExternalDN                     string                  `json:"external_dn,omitempty"`
	ExternalPasswordExpirationDate string                  `json:"external_password_expiration_date,omitempty"`
	ExternalSourceType             string                  `json:"external_source_type,omitempty"`
	ExternallyManaged              bool                    `json:"externally_managed,omitempty"`
	FirstName                      string                  `json:"firstname,omitempty"`
	JobTitle                       string                  `json:"jobTitle,omitempty"`
	LastName                       string                  `json:"lastname,omitempty"`
	LDAPBindingUser                bool                    `json:"ldap_binding_user,omitempty"`
	Location                       string                  `json:"location,omitempty"`
	ManagedAppleID                 string                  `json:"managedAppleId,omitempty"`
	Manager                        string                  `json:"manager,omitempty"`
	MFA                            *UserMFA                `json:"mfa,omitempty"`
	MFAEnrollment                  *UserMFAEnrollment      `json:"mfaEnrollment,omitempty"`
	MiddleName                     string                  `json:"middlename,omitempty"`
	Organization                   string                  `json:"organization,omitempty"`
	PasswordDate                   *string                 `json:"password_date,omitempty"`
	PasswordExpirationDate         *string                 `json:"password_expiration_date,omitempty"`
	PasswordExpired                bool                    `json:"password_expired,omitempty"`
	PasswordNeverExpires           bool                    `json:"password_never_expires,omitempty"`
	PasswordlessSudo               bool                    `json:"passwordless_sudo,omitempty"`
	PhoneNumbers                   []UserPhoneNumber       `json:"phoneNumbers,omitempty"`
	PublicKey                      string                  `json:"public_key,omitempty"`
	RecoveryEmail                  *UserRecoveryEmail      `json:"recoveryEmail,omitempty"`
	Relationships                  []UserRelationship      `json:"relationships,omitempty"`
	RestrictedFields               []any                   `json:"restrictedFields,omitempty"`
	SambaServiceUser               bool                    `json:"samba_service_user,omitempty"`
	SSHKeys                        []UserSSHKey            `json:"ssh_keys,omitempty"`
	State                          UserState               `json:"state,omitempty"`
	Sudo                           bool                    `json:"sudo,omitempty"`
	Suspended                      bool                    `json:"suspended,omitempty"`
	Tags                           []string                `json:"tags,omitempty"`
	TOTPEnabled                    bool                    `json:"totp_enabled,omitempty"`
	UnixGUID                       int                     `json:"unix_guid,omitempty"`
	UnixUID                        int                     `json:"unix_uid,omitempty"`
	Username                       string                  `json:"username,omitempty"`
}
