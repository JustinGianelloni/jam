package system

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/internal/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List systems",
	Args:  cobra.ArbitraryArgs,
	RunE:  listSystems,
}

func init() {
	listCmd.Flags().BoolP("windows", "w", false, "Only list Windows devices")
	listCmd.Flags().BoolP("macos", "m", false, "Only list macOS devices")
	listCmd.Flags().BoolP("linux", "l", false, "Only list Linux devices")
	listCmd.Flags().BoolP("ios", "i", false, "Only list iOS devices")
	listCmd.Flags().BoolP("ipados", "p", false, "Only list iPadOS devices")
	listCmd.Flags().BoolP("android", "a", false, "Only list Android devices")

	listCmd.Flags().BoolP("show-remote-ip", "I", false, "Show Remote IP Address")
	listCmd.Flags().BoolP("show-hostname", "H", false, "Show hostname")

	listCmd.Flags().Bool("json", false, "Return results as JSON")
	listCmd.Flags().String("csv", "", "Save the results to the provided CSV file")
}

func listSystems(cmd *cobra.Command, args []string) error {
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	argFilters, err := common.ParseV1FilterArgs(args)
	if err != nil {
		return fmt.Errorf("Error parsing filters: %w", err)
	}
	flagFilters, err := parseFilterFlags(cmd)
	if err != nil {
		return fmt.Errorf("Error parsing filters: %w", err)
	}
	filters := append(argFilters, flagFilters...)
	systems, err := client.ListSystems(cmd.Context(), filters)
	if err != nil {
		return fmt.Errorf("Error fetching system list: %w", err)
	}
	j, _ := cmd.Flags().GetBool("json")
	csv, _ := cmd.Flags().GetString("csv")
	if term.IsTerminal(os.Stdout.Fd()) {
		if j {
			data, err := json.MarshalIndent(systems, "", "  ")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			return cli.PrintJSON(data)
		} else {
			return cli.PrintSystemsTable(systems, common.GetSystemsColumns(cmd), csv)
		}
	} else {
		if j {
			data, err := json.MarshalIndent(systems, "", "  ")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			fmt.Println(string(data))
			return nil
		} else {
			for i := range systems {
				fmt.Println(systems[i].ID)
			}
			return nil
		}
	}
}

func parseFilterFlags(cmd *cobra.Command) ([]models.V1Filter, error) {
	filters := make([]models.V1Filter, 0)
	var visitErr error
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "windows":
			filter, err := models.NewV1Filter("osFamily:$eq:windows")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "macos":
			filter, err := models.NewV1Filter("osFamily:$eq:darwin")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "linux":
			filter, err := models.NewV1Filter("osFamily:$eq:linux")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "ios":
			filter, err := models.NewV1Filter("os:$eq:iOS")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "ipados":
			filter, err := models.NewV1Filter("os:$eq:iPadOS")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "android":
			filter, err := models.NewV1Filter("osFamily:$eq:android")
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		}
	})
	return filters, visitErr
}
