package group

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List groups",
	Args:  cobra.ArbitraryArgs,
	RunE:  listGroups,
}

func init() {
	listCmd.Flags().StringP("name", "n", "", "Filter results by group name.")

	listCmd.Flags().BoolP("show-description", "D", false, "Show group description")

	listCmd.Flags().Bool("json", false, "Return results as JSON")
	listCmd.Flags().String("csv", "", "Save the results to the provided CSV file")
}

func listGroups(cmd *cobra.Command, args []string) error {
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	argFilters, err := common.ParseV2FilterArgs(args)
	if err != nil {
		return fmt.Errorf("Error parsing filters: %w", err)
	}
	flagFilters, err := parseFilterFlags(cmd)
	if err != nil {
		return fmt.Errorf("Error parsing filters: %w", err)
	}
	filters := append(argFilters, flagFilters...)
	groups, err := client.ListUserGroups(cmd.Context(), filters)
	if err != nil {
		return fmt.Errorf("Error fetching group list: %w", err)
	}
	j, _ := cmd.Flags().GetBool("json")
	csv, _ := cmd.Flags().GetString("csv")
	if term.IsTerminal(os.Stdout.Fd()) {
		if j {
			data, err := json.MarshalIndent(groups, "", "  ")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			return cli.PrintJSON(data)
		} else {
			return cli.PrintGroupsTable(groups, common.GetGroupsColumns(cmd), csv)
		}
	} else {
		if j {
			data, err := json.MarshalIndent(groups, "", "")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			fmt.Println(string(data))
			return nil
		} else {
			for i := range groups {
				fmt.Println(groups[i].ID)
			}
			return nil
		}
	}
}

func parseFilterFlags(cmd *cobra.Command) ([]models.V2Filter, error) {
	filters := make([]models.V2Filter, 0)
	var visitErr error
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "name":
			filter, err := models.NewV2Filter(fmt.Sprintf("name:search:%s", f.Value.String()))
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		}
	})
	return filters, visitErr
}
