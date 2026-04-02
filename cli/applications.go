package cli

import (
	"fmt"
	"os"
	"reflect"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/table"
	"github.com/justingianelloni/jam/models"
)

func PrintAppsTable(apps []models.Application, columns []string, filename string) error {
	rows := getAppsTableRows(apps, columns)
	t := table.New().
		Wrap(false).
		Border(lipgloss.NormalBorder()).
		Headers(columns...).
		Rows(rows...).
		StyleFunc(func(row, col int) lipgloss.Style {
			if row == table.HeaderRow {
				return tableHeaderStyle
			}
			if col == 0 {
				return idColStyle
			}
			return tableCellStyle
		})
	if err := RenderTable(t); err != nil {
		return err
	}
	if filename != "" {
		err := SaveTableToCSV(rows, columns, filename)
		if err != nil {
			return fmt.Errorf("Saving to CSV: %w", err)
		}
		fmt.Fprintf(os.Stderr, "Results saved to CSV file: %s\n", filename)
	}
	return nil
}

func getAppsTableRows(apps []models.Application, columns []string) [][]string {
	rows := make([][]string, len(apps))
	for y, app := range apps {
		rows[y] = make([]string, len(columns))
		for x, column := range columns {
			rows[y][x] = reflect.ValueOf(app).FieldByName(column).String()
		}
	}
	return rows
}
