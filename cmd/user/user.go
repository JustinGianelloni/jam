package user

import (
	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "user",
	Short: "Manager users",
}

func init() {
	Cmd.AddCommand(listCmd)
	Cmd.AddCommand(getCmd)
	Cmd.AddCommand(findCmd)
	Cmd.AddCommand(boundSystemsCmd)
}
