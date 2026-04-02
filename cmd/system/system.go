package system

import (
	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "system",
	Short: "Manage systems",
}

func init() {
	Cmd.AddCommand(listCmd)
	Cmd.AddCommand(getCmd)
	Cmd.AddCommand(findCmd)
	Cmd.AddCommand(boundUsersCmd)
}
