package app

import (
	"github.com/justingianelloni/jam/cmd/app/group"
	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "app",
	Short: "Manage applications",
}

func init() {
	Cmd.AddCommand(group.Cmd)

	Cmd.AddCommand(listCmd)
}
