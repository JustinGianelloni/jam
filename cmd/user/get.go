package user

import (
	"fmt"
	"strings"
	"sync"

	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/internal/config"
	"github.com/justingianelloni/jam/models"
	"github.com/spf13/cobra"
)

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Get users",
	Args:  cobra.ArbitraryArgs,
	RunE:  getUsers,
}

func init() {
	getCmd.Flags().BoolP("show-department", "D", false, "Show department column")
	getCmd.Flags().BoolP("show-cost-center", "C", false, "Show cost center column")
	getCmd.Flags().BoolP("show-job-title", "J", false, "Show job title column")
	getCmd.Flags().BoolP("show-state", "S", false, "Show account state")
	getCmd.Flags().BoolP("show-type", "T", false, "Show employee type")
}

func getUsers(cmd *cobra.Command, args []string) error {
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
		num  int
		user models.User
		err  error
	}
	users := make([]models.User, len(args))
	results := make(chan result, len(args))
	var wg sync.WaitGroup
	for i := range args {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			user, err := client.GetUser(cmd.Context(), args[i])
			if err != nil {
				results <- result{num: i, err: err}
				return
			}
			results <- result{num: i, user: *user}
		}(i)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return fmt.Errorf("Fetching user: %s", args[r.num])
		}
		users[r.num] = r.user
	}
	switch len(users) {
	case 0:
		return fmt.Errorf("No users found for given args: %s", strings.Join(args, ", "))
	case 1:
		manager, err := client.GetUser(cmd.Context(), users[0].Manager)
		if err != nil {
			return fmt.Errorf("Error fetching manager for user: %s", users[0].Email)
		}
		manager_name := fmt.Sprintf("%s, %s", manager.LastName, manager.FirstName)
		return cli.PrintUserTable(users[0], manager_name)
	default:
		return cli.PrintUsersTable(users, common.GetUsersColumns(cmd), "")
	}
}
