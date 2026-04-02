package user

import (
	"fmt"
	"os"
	"strings"

	"github.com/charmbracelet/x/term"
	"github.com/justingianelloni/jam/api"
	"github.com/justingianelloni/jam/cli"
	"github.com/justingianelloni/jam/cmd/common"
	"github.com/justingianelloni/jam/config"
	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
)

var findCmd = &cobra.Command{
	Use:   "find",
	Short: "Find users",
	Args:  cobra.ExactArgs(1),
	RunE:  findUsers,
}

func init() {
	findCmd.Flags().BoolP("firstname", "f", false, "Search first name")
	findCmd.Flags().BoolP("lastname", "l", false, "Search last name")
	findCmd.Flags().BoolP("email", "e", false, "Search email")
	findCmd.Flags().BoolP("alternate-email", "a", false, "Search alernate email")
	findCmd.Flags().BoolP("displayname", "d", false, "Search display name")
	findCmd.Flags().BoolP("username", "u", false, "Search username")

	findCmd.Flags().BoolP("show-department", "D", false, "Show department column")
	findCmd.Flags().BoolP("show-cost-center", "C", false, "Show cost center column")
	findCmd.Flags().BoolP("show-job-title", "J", false, "Show job title column")
	findCmd.Flags().BoolP("show-state", "S", false, "Show account state")
	findCmd.Flags().BoolP("show-type", "T", false, "Show employee type")
}

func findUsers(cmd *cobra.Command, args []string) error {
	creds, err := config.Load(cmd.Context())
	if err != nil {
		return fmt.Errorf("Error loading credentials: %w", err)
	}
	client := api.NewClient(creds)
	fields := parseFieldArgs(cmd)
	users, err := client.SearchUsers(cmd.Context(), args[0], fields)
	if err != nil {
		return fmt.Errorf("Error searching users: %w", err)
	}
	switch len(users) {
	case 0:
		return fmt.Errorf("No users found for query: %s, using fields: %s", args[0], strings.Join(fields, ", "))
	case 1:
		manager, err := client.GetUser(cmd.Context(), users[0].Manager)
		if err != nil {
			return fmt.Errorf("Error fetching manager for user: %s", users[0].Email)
		}
		managerName := fmt.Sprintf("%s, %s", manager.LastName, manager.FirstName)
		if term.IsTerminal(os.Stdout.Fd()) {
			return cli.PrintUserTable(users[0], managerName)
		} else {
			fmt.Println(users[0].ID)
			return nil
		}
	default:
		if term.IsTerminal(os.Stdout.Fd()) {
			return cli.PrintUsersTable(users, common.GetUsersColumns(cmd), "")
		} else {
			for i := range users {
				fmt.Println(users[i].ID)
			}
		}
		return nil
	}
}

func parseFieldArgs(cmd *cobra.Command) []string {
	fields := make([]string, 0)
	cmd.Flags().Visit(func(f *pflag.Flag) {
		switch f.Name {
		case "firstname":
			fields = append(fields, "firstname")
		case "lastname":
			fields = append(fields, "lastname")
		case "email":
			fields = append(fields, "email")
		case "alternate-email":
			fields = append(fields, "alernateEmail")
		case "displayname":
			fields = append(fields, "displayname")
		case "username":
			fields = append(fields, "username")
		}
	})
	if len(fields) == 0 {
		fields = []string{"firstname", "lastname", "email", "alternateEmail", "displayname", "username"}
	}
	return fields
}
