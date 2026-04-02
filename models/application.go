package models

type Application struct {
	ID           string `json:"id,omitempty"`
	Active       bool   `json:"active,omitempty"`
	DisplayLabel string `json:"displayLabel,omitempty"`
}
