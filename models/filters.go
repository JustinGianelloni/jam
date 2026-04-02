package models

import (
	"fmt"
	"slices"
	"strings"
)

var v1Operators = []string{
	"$eq",
	"$ne",
	"$gt",
	"$gte",
	"$lt",
	"$lte",
	"$regex",
	"$exists",
	"$in",
	"$nin",
}

var v2Operators = []string{
	"eq",
	"ne",
	"gt",
	"gte",
	"lt",
	"lte",
	"regex",
	"exists",
	"in",
	"nin",
	"between",
	"search",
}

type V1Filter string
type V2Filter string

func NewV1Filter(filter string) (V1Filter, error) {
	parts := strings.Split(strings.Trim(filter, " "), ":")
	if len(parts) != 3 {
		return "", fmt.Errorf("Invalid filter: %s", filter)
	}
	if !slices.Contains(v1Operators, parts[1]) {
		return "", fmt.Errorf("Invalid filter: %s", filter)
	}
	return V1Filter(filter), nil
}

func (filter V1Filter) String() string {
	return string(filter)
}

func NewV2Filter(filter string) (V2Filter, error) {
	parts := strings.Split(strings.Trim(filter, " "), ":")
	if len(parts) != 3 {
		return "", fmt.Errorf("Invalid filter: %s", filter)
	}
	if !slices.Contains(v2Operators, parts[1]) {
		return "", fmt.Errorf("Invalid filter: %s", filter)
	}
	return V2Filter(filter), nil
}

func (filter V2Filter) String() string {
	return string(filter)
}
