package cli

import (
	"fmt"
	"os"
	"reflect"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/table"
	"github.com/justingianelloni/jam/models"
)

func PrintUsersTable(users []models.User, columns []string, filename string) error {
	rows := getUsersTableRows(users, columns)
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
				case "ACTIVATED":
					return activatedStateStyle.Width(11)
				case "SUSPENDED":
					return suspendedStateStyle.Width(11)
				case "STAGED":
					return stagedStateStyle.Width(11)
				}
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

func getUsersTableRows(users []models.User, columns []string) [][]string {
	rows := make([][]string, len(users))
	for y, user := range users {
		rows[y] = make([]string, len(columns))
		for x, column := range columns {
			rows[y][x] = reflect.ValueOf(user).FieldByName(column).String()
		}
	}
	return rows
}

var userTableRows = []string{
	"ID",
	"EmployeeIdentifier",
	"State",
	"EmployeeType",
	"Name",
	"DisplayName",
	"Username",
	"Email",
	"AlternateEmail",
	"JobTitle",
	"Department",
	"CostCenter",
	"Manager",
}

func PrintUserTable(user models.User, manager string) error {
	rows := getUserTableRows(user, manager)
	t := table.New().
		Rows(rows...).
		Wrap(false).
		StyleFunc(func(row, col int) lipgloss.Style {
			if col == 0 {
				return keyStyle
			}
			if rows[row][0] == "State" {
				switch rows[row][1] {
				case "ACTIVATED":
					return activatedStateStyle.Padding(0)
				case "SUSPENDED":
					return suspendedStateStyle.Padding(0)
				case "STAGED":
					return stagedStateStyle.Padding(0)
				}
			}
			return valueStyle
		})
	fmt.Println(t)
	return nil
}

func getUserTableRows(user models.User, manager string) [][]string {
	rows := make([][]string, len(userTableRows))
	for y := range userTableRows {
		rows[y] = make([]string, 2)
		rows[y][0] = userTableRows[y]
		switch userTableRows[y] {
		case "Manager":
			rows[y][1] = manager
		case "Name":
			rows[y][1] = fmt.Sprintf("%s, %s", user.LastName, user.FirstName)
		default:
			rows[y][1] = reflect.ValueOf(user).FieldByName(userTableRows[y]).String()
		}
	}
	return rows
}
