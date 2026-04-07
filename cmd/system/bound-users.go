package system

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

var boundUsersCmd = &cobra.Command{
	Use:   "bound-users",
	Short: "List bound users",
	Args:  cobra.ArbitraryArgs,
	RunE:  listBoundUsers,
}

func init() {
	boundUsersCmd.Flags().BoolP("show-department", "D", false, "Show department column")
	boundUsersCmd.Flags().BoolP("show-cost-center", "C", false, "Show cost center column")
	boundUsersCmd.Flags().BoolP("show-job-title", "J", false, "Show job title column")
	boundUsersCmd.Flags().BoolP("show-state", "S", false, "Show account state")
	boundUsersCmd.Flags().BoolP("show-type", "T", false, "Show employee type")
}

func listBoundUsers(cmd *cobra.Command, args []string) error {
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
	userIDs, err := client.ListBoundUsers(cmd.Context(), args[0])
	if err != nil {
		return fmt.Errorf("Error fetching bound users: %w", err)
	}
	if len(userIDs) == 0 {
		return fmt.Errorf("No users found for system with id: %s", args[0])
	}
	type result struct {
		num  int
		user models.User
		err  error
	}
	users := make([]models.User, len(userIDs))
	results := make(chan result, len(userIDs))
	var wg sync.WaitGroup
	for i := range userIDs {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			user, err := client.GetUser(cmd.Context(), userIDs[i])
			if err != nil {
				results <- result{num: i, err: err}
			}
			results <- result{num: i, user: *user}
		}(i)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return fmt.Errorf("Fetching user: %s", userIDs[r.num])
		}
		users[r.num] = r.user
	}
	if len(users) == 1 {
		manager, err := client.GetUser(cmd.Context(), users[0].Manager)
		if err != nil {
			return fmt.Errorf("Error getting manager for: %s", users[0].Email)
		}
		managerName := fmt.Sprintf("%s, %s", manager.LastName, manager.FirstName)
		return cli.PrintUserTable(users[0], managerName)
	} else {
		return cli.PrintUsersTable(users, common.GetUsersColumns(cmd), "")
	}
}
