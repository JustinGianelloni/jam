package member

import "github.com/spf13/cobra"

var Cmd = &cobra.Command{
	Use:   "member",
	Short: "Manage group members",
}

func init() {
	Cmd.AddCommand(listCmd)
}
