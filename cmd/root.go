package cmd

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"

	"github.com/justingianelloni/jam/cmd/app"
	"github.com/justingianelloni/jam/cmd/group"
	"github.com/justingianelloni/jam/cmd/system"
	"github.com/justingianelloni/jam/cmd/user"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/subosito/gotenv"
)

var rootCmd = &cobra.Command{
	Use:   "jam",
	Short: "jam",
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
