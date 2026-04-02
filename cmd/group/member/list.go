package member

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

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List group members",
	Args:  cobra.ArbitraryArgs,
	RunE:  listMembers,
}

func init() {
	listCmd.Flags().BoolP("show-department", "D", false, "Show department column")
	listCmd.Flags().BoolP("show-cost-center", "C", false, "Show cost center column")
	listCmd.Flags().BoolP("show-job-title", "J", false, "Show job title column")
	listCmd.Flags().BoolP("show-state", "S", false, "Show account state")
	listCmd.Flags().BoolP("show-type", "T", false, "Show employee type")

	listCmd.Flags().Bool("json", false, "Return results as JSON")
	listCmd.Flags().String("csv", "", "Save the results to the provided CSV file")
}

func listMembers(cmd *cobra.Command, args []string) error {
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
		num     int
		members []string
		err     error
	}
	type listResult struct {
		users []models.User
		err   error
	}
	results := make(chan result, len(args))
	listResults := make(chan listResult, 1)
	var wg sync.WaitGroup
	for i := range args {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			m, err := client.UserGroupMembers(cmd.Context(), args[i])
			if err != nil {
				results <- result{num: i, err: err}
				return
			}
			results <- result{num: i, members: m}
		}(i)
	}
	wg.Go(func() {
		u, err := client.ListUsers(cmd.Context(), nil)
		if err != nil {
			listResults <- listResult{err: err}
			return
		}
		listResults <- listResult{users: u}
	})
	wg.Wait()
	close(results)
	close(listResults)
	lr := <-listResults
	if lr.err != nil {
		return fmt.Errorf("Error fetching full user list: %w", err)
	}
	userMap := make(map[string]models.User, len(lr.users))
	for _, user := range lr.users {
		userMap[user.ID] = user
	}
	var allResults []result
	for r := range results {
		if r.err != nil {
			return fmt.Errorf("Fetching group members: %s", args[r.num])
		}
		allResults = append(allResults, r)
	}
	total := 0
	for _, r := range allResults {
		total += len(r.members)
	}
	seen := make(map[string]bool, total)
	var members []models.User
	for _, r := range allResults {
		for _, id := range r.members {
			if !seen[id] {
				seen[id] = true
				if m, ok := userMap[id]; ok {
					members = append(members, m)
				}
			}
		}
	}
	switch len(members) {
	case 0:
		return fmt.Errorf("No members found for the specified group(s): %s", strings.Join(args, ", "))
	case 1:
		manager, err := client.GetUser(cmd.Context(), members[0].Manager)
		if err != nil {
			return fmt.Errorf("Error fetching manager for user: %s", members[0].Email)
		}
		manager_name := fmt.Sprintf("%s, %s", manager.LastName, manager.FirstName)
		return cli.PrintUserTable(members[0], manager_name)
	default:
		return cli.PrintUsersTable(members, common.GetUsersColumns(cmd), "")
	}
}
