package models

type UserGroupAttributes struct {
	SambaEnabled bool                       `json:"sambaEnabled,omitempty"`
	PosixGroups  []UserGroupPosixGroupEntry `json:"posixGroups,omitempty"`
}

type UserGroupPosixGroupEntry struct {
	ID   int    `json:"id,omitempty"`
	Name string `json:"name,omitempty"`
}

type UserGroup struct {
	ID          string               `json:"id,omitempty"`
	Name        string               `json:"name,omitempty"`
	Type        string               `json:"type,omitempty"`
	Description string               `json:"description"`
	Attributes  *UserGroupAttributes `json:"attributes,omitempty"`
}
