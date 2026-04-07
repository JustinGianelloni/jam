package cmd

import (
	"fmt"

	"github.com/justingianelloni/jam/internal/update"
	"github.com/spf13/cobra"
)

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print the current version of jam",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("jam %s\n", update.Version)
	},
}
