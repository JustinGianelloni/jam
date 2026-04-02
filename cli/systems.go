package cli

import (
	"fmt"
	"os"
	"reflect"
	"strconv"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/table"
	"github.com/justingianelloni/jam/models"
)

func PrintSystemsTable(systems []models.System, columns []string, filename string) error {
	rows := getSystemsTableRows(systems, columns)
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
			if col == 1 {
				switch rows[row][col] {
				case "true":
					return activatedStateStyle.Width(8)
				case "false":
					return suspendedStateStyle.Width(8)
				}
			}
			if col == 2 {
				return tableCellStyle.Width(16)
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

func getSystemsTableRows(systems []models.System, columns []string) [][]string {
	rows := make([][]string, len(systems))
	for y, system := range systems {
		rows[y] = make([]string, len(columns))
		for x, column := range columns {
			switch column {
			case "Active":
				rows[y][x] = strconv.FormatBool(system.Active)
			case "LastContact":
				if system.LastContact != nil {
					rows[y][x] = system.LastContact.Local().Format(time.RFC822)
				} else {
					rows[y][x] = "N/A"
				}
			case "OSVersion":
				if system.OSVersionDetail != nil {
					rows[y][x] = system.OSVersionDetail.Version
				} else {
					rows[y][x] = "N/A"
				}
			default:
				rows[y][x] = reflect.ValueOf(system).FieldByName(column).String()
			}
		}
	}
	return rows
}

var systemTableRows = []string{
	"ID",
	"Active",
	"SerialNumber",
	"Hostname",
	"LastContact",
	"OS",
	"RemoteIP",
	"OSVersion",
}

func PrintSystemTable(system models.System) error {
	rows := getSystemTableRows(system)
	t := table.New().
		Rows(rows...).
		Wrap(false).
		StyleFunc(func(row, col int) lipgloss.Style {
			if col == 0 {
				return keyStyle
			}
			if rows[row][0] == "Active" {
				if rows[row][1] == "true" {
					return activatedStateStyle.Padding(0)
				} else {
					return suspendedStateStyle.Padding(0)
				}
			}
			return valueStyle
		})
	fmt.Println(t)
	return nil
}

func getSystemTableRows(system models.System) [][]string {
	rows := make([][]string, len(systemTableRows))
	for y := range systemTableRows {
		rows[y] = make([]string, 2)
		rows[y][0] = systemTableRows[y]
		switch systemTableRows[y] {
		case "Active":
			rows[y][1] = strconv.FormatBool(system.Active)
		case "LastContact":
			if system.LastContact != nil {
				rows[y][1] = system.LastContact.Local().Format(time.RFC822)
			} else {
				rows[y][1] = "N/A"
			}
		case "OSVersion":
			if system.OSVersionDetail != nil {
				rows[y][1] = system.OSVersionDetail.Version
			} else {
				rows[y][1] = "N/A"
			}
		default:
			rows[y][1] = reflect.ValueOf(system).FieldByName(systemTableRows[y]).String()
		}
	}
	return rows
}
