package update

import (
	"encoding/json"
	"os"
	"path/filepath"
	"time"
)

const cacheTTL = 1 * time.Hour

type cache struct {
	LatestVersion string    `json:"latest_version"`
	CheckedAt     time.Time `json:"checked_at"`
}

func cachePath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "jam", ".update-check")
}

// LoadCache reads the cached version check result.
func LoadCache() (latestVersion string, fresh bool) {
	data, err := os.ReadFile(cachePath())
	if err != nil {
		return "", false
	}
	var c cache
	if err := json.Unmarshal(data, &c); err != nil {
		return "", false
	}
	return c.LatestVersion, time.Since(c.CheckedAt) < cacheTTL
}

// SaveCache writes the latest version to the cache file.
func SaveCache(version string) {
	c := cache{LatestVersion: version, CheckedAt: time.Now()}
	data, err := json.Marshal(c)
	if err != nil {
		return
	}
	_ = os.WriteFile(cachePath(), data, 0644)
}
