package cmd

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"time"

	"github.com/justingianelloni/jam/internal/update"
	"github.com/spf13/cobra"
)

var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "Update jam to the latest version",
	RunE:  runUpdate,
}

func runUpdate(cmd *cobra.Command, args []string) error {
	ctx, cancel := context.WithTimeout(cmd.Context(), 30*time.Second)
	defer cancel()
	fmt.Println("Checking for updates...")
	rel, err := update.CheckLatest(ctx)
	if err != nil {
		return fmt.Errorf("checking for updates: %w", err)
	}
	if !update.IsNewer(update.Version, rel.TagName) {
		fmt.Printf("Already up to date (%s)\n", update.Version)
		return nil
	}
	downloadURL, err := rel.AssetForPlatform()
	if err != nil {
		return err
	}
	fmt.Printf("Downloading %s...\n", rel.TagName)
	execPath, err := os.Executable()
	if err != nil {
		return fmt.Errorf("finding executable path: %w", err)
	}
	execPath, err = filepath.EvalSymlinks(execPath)
	if err != nil {
		return fmt.Errorf("resolving executable path: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, downloadURL, nil)
	if err != nil {
		return err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("downloading binary: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("download returned HTTP %d", resp.StatusCode)
	}
	// Write to temp file in the same directory for atomic rename
	dir := filepath.Dir(execPath)
	tmp, err := os.CreateTemp(dir, "jam-update-*")
	if err != nil {
		return fmt.Errorf("creating temp file: %w", err)
	}
	tmpPath := tmp.Name()
	defer os.Remove(tmpPath)
	if _, err := io.Copy(tmp, resp.Body); err != nil {
		tmp.Close()
		return fmt.Errorf("writing binary: %w", err)
	}
	tmp.Close()
	if err := os.Chmod(tmpPath, 0755); err != nil {
		return fmt.Errorf("setting permissions: %w", err)
	}
	// On Windows, rename the current binary out of the way first
	if runtime.GOOS == "windows" {
		oldPath := execPath + ".old"
		_ = os.Remove(oldPath)
		if err := os.Rename(execPath, oldPath); err != nil {
			return fmt.Errorf("moving old binary: %w", err)
		}
	}
	if err := os.Rename(tmpPath, execPath); err != nil {
		return fmt.Errorf("replacing binary: %w", err)
	}
	update.SaveCache(rel.TagName)
	fmt.Printf("Updated jam %s -> %s\n", update.Version, rel.TagName)
	return nil
}
