package group

import (
	"github.com/justingianelloni/jam/cmd/group/member"
	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "group",
	Short: "Manage groups",
}

func init() {
	Cmd.AddCommand(member.Cmd)

	Cmd.AddCommand(listCmd)
}
