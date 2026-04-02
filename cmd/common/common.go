package common

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

var DefaultSystemColumns = []string{
	"ID",
	"Active",
	"SerialNumber",
	"LastContact",
	"OS",
	"OSVersion",
}

var DefaultUserColumns = []string{
	"ID",
	"State",
	"Email",
}

var DefaultGroupsColumns = []string{
	"ID",
	"Name",
}

var DefaultAppsColumns = []string{
	"ID",
	"DisplayLabel",
}

type State string

const (
	StateActive    State = "ACTIVATED"
	StateSuspended State = "SUSPENDED"
	StateStaged    State = "STAGED"
)

var validStates = []State{StateActive, StateSuspended, StateStaged}

func (s *State) String() string { return string(*s) }
func (s *State) Type() string   { return "state" }
func (s *State) Set(v string) error {
	for _, valid := range validStates {
		if strings.EqualFold(v, string(valid)) {
			*s = valid
			return nil
		}
	}
	return fmt.Errorf("must be one of: %v", validStates)
}

func ParseV1FilterArgs(args []string) ([]models.V1Filter, error) {
	filters := make([]models.V1Filter, len(args))
	for i, arg := range args {
		f, err := models.NewV1Filter(arg)
		if err != nil {
			return nil, fmt.Errorf("Error building filters: %w", err)
		}
		filters[i] = f
	}
	return filters, nil
}

func ParseV2FilterArgs(args []string) ([]models.V2Filter, error) {
	filters := make([]models.V2Filter, len(args))
	for i, arg := range args {
		f, err := models.NewV2Filter(arg)
		if err != nil {
			return nil, fmt.Errorf("Error building filters: %w", err)
		}
		filters[i] = f
	}
	return filters, nil
}

func ResolveArgs(args []string) ([]string, error) {
	if !term.IsTerminal(os.Stdin.Fd()) {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			line := strings.TrimSpace(scanner.Text())
			if line != "" {
				args = append(args, line)
			}
		}
		if err := scanner.Err(); err != nil {
			return nil, fmt.Errorf("Reading stdin: %w", err)
		}
	}
	if len(args) == 0 {
		return nil, fmt.Errorf("No arguments specified")
	}
	return args, nil
}

func GetUsersColumns(cmd *cobra.Command) []string {
	columns := DefaultUserColumns
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "show-department":
			columns = append(columns, "Department")
		case "show-cost-center":
			columns = append(columns, "CostCenter")
		case "show-job-title":
			columns = append(columns, "JobTitle")
		case "show-state":
			columns = append(columns, "State")
		case "show-type":
			columns = append(columns, "EmployeeType")
		}
	})
	return columns
}

func GetSystemsColumns(cmd *cobra.Command) []string {
	columns := DefaultSystemColumns
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "show-remote-ip":
			columns = append(columns, "RemoteIP")
		case "show-hostname":
			columns = append(columns, "Hostname")
		}
	})
	return columns
}

func GetGroupsColumns(cmd *cobra.Command) []string {
	columns := DefaultGroupsColumns
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "show-description":
			columns = append(columns, "Description")
		}
	})
	return columns
}

func GetAppsColumns(cmd *cobra.Command) []string {
	columns := DefaultAppsColumns
	return columns
}
