package system

import (
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/internal/config"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

var findCmd = &cobra.Command{
	Use:   "find",
	Short: "Find systems",
	Args:  cobra.ExactArgs(1),
	RunE:  findSystems,
}

func init() {
	findCmd.Flags().BoolP("serial", "s", false, "Search serial number")
	findCmd.Flags().BoolP("hostname", "n", false, "Search hostname")
	findCmd.Flags().BoolP("ip", "i", false, "Search Remote IP")

	findCmd.Flags().BoolP("show-remote-ip", "I", false, "Show Remote IP Address")
	findCmd.Flags().BoolP("show-hostname", "H", false, "Show hostname")
}

func findSystems(cmd *cobra.Command, args []string) error {
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	fields := parseFieldArgs(cmd)
	systems, err := client.SearchSystems(cmd.Context(), args[0], fields)
	if err != nil {
		return fmt.Errorf("Error searching systems: %w", err)
	}
	switch len(systems) {
	case 0:
		return fmt.Errorf("No systems found for query: %s, using fields: %s", args[0], strings.Join(fields, ", "))
	case 1:
		if term.IsTerminal(os.Stdout.Fd()) {
			return cli.PrintSystemTable(systems[0])
		} else {
			fmt.Println(systems[0].ID)
			return nil
		}
	default:
		if term.IsTerminal(os.Stdout.Fd()) {
			return cli.PrintSystemsTable(systems, common.GetSystemsColumns(cmd), "")
		} else {
			for i := range systems {
				fmt.Println(systems[i].ID)
			}
		}
		return nil
	}
}

func parseFieldArgs(cmd *cobra.Command) []string {
	fields := make([]string, 0)
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "serial":
			fields = append(fields, "serialNumber")
		case "hostname":
			fields = append(fields, "hostname")
		case "ip":
			fields = append(fields, "remoteIP")
		}
	})
	if len(fields) == 0 {
		fields = []string{"serialNumber", "hostname", "remoteIP"}
	}
	return fields
}
