package system

import (
	"fmt"
	"strings"
	"sync"

	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
)

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Get systems",
	Args:  cobra.ArbitraryArgs,
	RunE:  getSystems,
}

func init() {
	getCmd.Flags().BoolP("show-remote-ip", "I", false, "Show Remote IP Address")
	getCmd.Flags().BoolP("show-hostname", "H", false, "Show hostname")
}

func getSystems(cmd *cobra.Command, args []string) error {
	args, err := common.ResolveArgs(args)
	if err != nil {
		return fmt.Errorf("Error resolving args: %w", err)
	}
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	type result struct {
		num    int
		system models.System
		err    error
	}
	systems := make([]models.System, len(args))
	results := make(chan result, len(args))
	var wg sync.WaitGroup
	for i := range args {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			system, err := client.GetSystem(cmd.Context(), args[i])
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
			return fmt.Errorf("Fetching system: %s", args[r.num])
		}
		systems[r.num] = r.system
	}
	switch len(systems) {
	case 0:
		return fmt.Errorf("No systems found for the given ars: %s", strings.Join(args, ", "))
	case 1:
		return cli.PrintSystemTable(systems[0])
	default:
		return cli.PrintSystemsTable(systems, common.GetSystemsColumns(cmd), "")
	}
}
