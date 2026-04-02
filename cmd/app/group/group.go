package group

import "github.com/spf13/cobra"

var Cmd = &cobra.Command{
	Use:   "group",
	Short: "Manage application groups",
}

func init() {
	Cmd.AddCommand(listCmd)
}
