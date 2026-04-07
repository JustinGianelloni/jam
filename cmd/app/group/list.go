package group

import (
	"encoding/json"
	"fmt"
	"os"
	"sync"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/internal/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List application groups",
	Args:  cobra.ArbitraryArgs,
	RunE:  listGroups,
}

func init() {
	listCmd.Flags().Bool("json", false, "Return results as JSON")
	listCmd.Flags().String("csv", "", "Save the results to the provided CSV file")
}

func listGroups(cmd *cobra.Command, args []string) error {
	args, err := common.ResolveArgs(args)
	if err != nil {
		return fmt.Errorf("Error resolving args: %w", err)
	}
	if len(args) > 1 {
		return fmt.Errorf("Only one application may be specified at a time.")
	}
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	type result struct {
		groups []string
		err    error
	}
	type listResult struct {
		groups []models.UserGroup
		err    error
	}
	results := make(chan result, 1)
	listResults := make(chan listResult, 1)
	var wg sync.WaitGroup
	wg.Go(func() {
		g, err := client.ListAppGroups(cmd.Context(), args[0])
		if err != nil {
			results <- result{err: err}
			return
		}
		results <- result{groups: g}
	})
	wg.Go(func() {
		g, err := client.ListUserGroups(cmd.Context(), nil)
		if err != nil {
			listResults <- listResult{err: err}
			return
		}
		listResults <- listResult{groups: g}
	})
	wg.Wait()
	close(results)
	close(listResults)
	lr := <-listResults
	if lr.err != nil {
		return fmt.Errorf("Error fetching full usergroup list: %w", err)
	}
	groupMap := make(map[string]models.UserGroup, len(lr.groups))
	for _, group := range lr.groups {
		groupMap[group.ID] = group
	}
	allResults := <-results
	if allResults.err != nil {
		return fmt.Errorf("Fetching groups: %w", err)
	}
	groups := make([]models.UserGroup, 0, len(allResults.groups))
	for _, g := range allResults.groups {
		if g, ok := groupMap[g]; ok {
			groups = append(groups, g)
		}
	}
	if len(groups) == 0 {
		return fmt.Errorf("No groups found bound to this application: %s", args[0])
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
			data, err := json.MarshalIndent(groups, "", "  ")
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
