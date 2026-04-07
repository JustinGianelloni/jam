package user

import (
	"fmt"
	"sync"

	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/internal/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
)

var boundSystemsCmd = &cobra.Command{
	Use:   "bound-systems",
	Short: "List bound systems",
	Args:  cobra.ArbitraryArgs,
	RunE:  listBoundSystems,
}

func init() {
	boundSystemsCmd.Flags().BoolP("show-remote-ip", "I", false, "Show Remote IP Address")
	boundSystemsCmd.Flags().BoolP("show-hostname", "H", false, "Show hostname")
}

func listBoundSystems(cmd *cobra.Command, args []string) error {
	args, err := common.ResolveArgs(args)
	if err != nil {
		return fmt.Errorf("Error parsing arguments: %w", err)
	}
	if len(args) > 1 {
		return fmt.Errorf("Only one user ID may be passed as an argument.")
	}
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	systemIDs, err := client.ListBoundSystems(cmd.Context(), args[0])
	if err != nil {
		return fmt.Errorf("Error fetching bound systems: %w", err)
	}
	if len(systemIDs) == 0 {
		return fmt.Errorf("No systems found for user with id: %s", args[0])
	}
	type result struct {
		num    int
		system models.System
		err    error
	}
	systems := make([]models.System, len(systemIDs))
	results := make(chan result, len(systemIDs))
	var wg sync.WaitGroup
	for i := range systemIDs {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			system, err := client.GetSystem(cmd.Context(), systemIDs[i])
			if err != nil {
				results <- result{num: i, err: err}
				return
			}
			results <- result{num: i, system: *system}
		}(i)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return fmt.Errorf("Fetching system: %s", systemIDs[r.num])
		}
		systems[r.num] = r.system
	}
	if len(systems) == 1 {
		return cli.PrintSystemTable(systems[0])
	} else {
		return cli.PrintSystemsTable(systems, common.GetSystemsColumns(cmd), "")
	}
}
