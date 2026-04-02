package cli

import (
	"encoding/csv"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/charmbracelet/glamour"
	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/table"
	"github.com/charmbracelet/x/term"
)

func PrintJSON(data []byte) error {
	out, err := glamour.Render("```json\n"+string(data)+"\n```", "dark")
	if err != nil {
		return err
	}
	fmt.Println(out)
	return nil
}

func SaveTableToCSV(rows [][]string, headers []string, filename string) error {
	if strings.HasPrefix(filename, "~") {
		home, _ := os.UserHomeDir()
		filename = filepath.Join(home, filename[1:])
	}
	path, err := filepath.Abs(filename)
	if err != nil {
		return fmt.Errorf("Building path: %w", err)
	}
	file, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("Creating file: %w", err)
	}
	defer file.Close()
	w := csv.NewWriter(file)
	w.Write(headers)
	for _, row := range rows {
		w.Write(row)
	}
	w.Flush()
	return w.Error()
}

func RenderTable(t *table.Table) error {
	w, _, err := term.GetSize(os.Stdout.Fd())
	if err != nil {
		return fmt.Errorf("Rendering table: %w", err)
	}
	rendered := t.Render()
	if lipgloss.Width(rendered) > w {
		t = t.Width(w)
		rendered = t.Render()
	}
	fmt.Println(rendered)
	return nil
}
