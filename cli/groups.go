package cli

import (
	"fmt"
	"os"
	"reflect"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/table"
	"github.com/justingianelloni/jam/models"
)

func PrintGroupsTable(groups []models.UserGroup, columns []string, filename string) error {
	rows := getGroupsTableRows(groups, columns)
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

func getGroupsTableRows(groups []models.UserGroup, columns []string) [][]string {
	rows := make([][]string, len(groups))
	for y, group := range groups {
		rows[y] = make([]string, len(columns))
		for x, column := range columns {
			rows[y][x] = reflect.ValueOf(group).FieldByName(column).String()
		}
	}
	return rows
}
