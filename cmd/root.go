package cmd

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"time"

	"github.com/justingianelloni/jam/cmd/app"
	"github.com/justingianelloni/jam/cmd/group"
	"github.com/justingianelloni/jam/cmd/system"
	"github.com/justingianelloni/jam/cmd/user"
	"github.com/justingianelloni/jam/internal/update"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/subosito/gotenv"
)

var updateResult chan string

var rootCmd = &cobra.Command{
	Use:   "jam",
	Short: "jam",
	PersistentPreRun: func(cmd *cobra.Command, args []string) {
		if cmd.Name() == "version" || cmd.Name() == "update" {
			return
		}
		updateResult = make(chan string, 1)
		go func() {
			latest, fresh := update.LoadCache()
			if fresh {
				if update.IsNewer(update.Version, latest) {
					updateResult <- latest
				}
				return
			}
			ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()
			rel, err := update.CheckLatest(ctx)
			if err != nil {
				return
			}
			update.SaveCache(rel.TagName)
			if update.IsNewer(update.Version, rel.TagName) {
				updateResult <- rel.TagName
			}
		}()
	},
	PersistentPostRun: func(cmd *cobra.Command, args []string) {
		if updateResult == nil {
			return
		}
		select {
		case latest := <-updateResult:
			fmt.Fprintf(os.Stderr, "\nA new version of jam is available: %s -> %s\nRun 'jam update' to update.\n", update.Version, latest)
		default:
		}
	},
}

func Execute() {
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()
	if err := rootCmd.ExecuteContext(ctx); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	initConfig()
	rootCmd.AddCommand(user.Cmd)
	rootCmd.AddCommand(system.Cmd)
	rootCmd.AddCommand(group.Cmd)
	rootCmd.AddCommand(app.Cmd)
	rootCmd.AddCommand(versionCmd)
	rootCmd.AddCommand(updateCmd)
}

func initConfig() {
	home, err := os.UserHomeDir()
	if err == nil {
		_ = gotenv.Load(filepath.Join(home, ".config", "jam", ".env"))
	}
	viper.AutomaticEnv()
	viper.SetConfigName("config")
	viper.SetConfigType("json")
	if home != "" {
		viper.AddConfigPath(filepath.Join(home, ".config", "jam"))
	}
	_ = viper.ReadInConfig()
}
