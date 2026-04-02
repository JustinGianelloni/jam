package user

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
	Short: "List users",
	Args:  cobra.ArbitraryArgs,
	RunE:  listUsers,
}

var stateFlag common.State

func init() {
	listCmd.Flags().StringP("department", "d", "", "Filter by department")
	listCmd.Flags().StringP("cost-center", "c", "", "Filter by cost center")
	listCmd.Flags().StringP("job-title", "j", "", "Filter by job title")
	listCmd.Flags().VarP(&stateFlag, "state", "s", "Filter by account state")
	listCmd.Flags().StringP("type", "t", "", "Filter by employee type")

	listCmd.Flags().BoolP("show-department", "D", false, "Show department column")
	listCmd.Flags().BoolP("show-cost-center", "C", false, "Show cost center column")
	listCmd.Flags().BoolP("show-job-title", "J", false, "Show job title column")
	listCmd.Flags().BoolP("show-state", "S", false, "Show account state")
	listCmd.Flags().BoolP("show-type", "T", false, "Show employee type")

	listCmd.Flags().Bool("json", false, "Return results as JSON")
	listCmd.Flags().String("csv", "", "Save the results to the provided CSV file")
}

func listUsers(cmd *cobra.Command, args []string) error {
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
	users, err := client.ListUsers(cmd.Context(), filters)
	if err != nil {
		return fmt.Errorf("Error fetching user list: %w", err)
	}
	j, _ := cmd.Flags().GetBool("json")
	csv, _ := cmd.Flags().GetString("csv")
	if term.IsTerminal(os.Stdout.Fd()) {
		if j {
			data, err := json.MarshalIndent(users, "", "  ")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			return cli.PrintJSON(data)
		} else {
			return cli.PrintUsersTable(users, common.GetUsersColumns(cmd), csv)
		}
	} else {
		if j {
			data, err := json.MarshalIndent(users, "", "  ")
			if err != nil {
				return fmt.Errorf("Error parsing json: %w", err)
			}
			fmt.Println(string(data))
			return nil
		} else {
			for i := range users {
				fmt.Println(users[i].ID)
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
		case "department":
			filter, err := models.NewV1Filter(fmt.Sprintf("department:$eq:%s", f.Value.String()))
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "cost-center":
			filter, err := models.NewV1Filter(fmt.Sprintf("costCenter:$eq:%s", f.Value.String()))
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "job-title":
			filter, err := models.NewV1Filter(fmt.Sprintf("jobTitle:$eq:%s", f.Value.String()))
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		case "type":
			filter, err := models.NewV1Filter(fmt.Sprintf("state:$eq:%s", f.Value.String()))
			if err != nil {
				visitErr = fmt.Errorf("Error building filters: %w", err)
				return
			}
			filters = append(filters, filter)
		}
	})
	return filters, visitErr
}
